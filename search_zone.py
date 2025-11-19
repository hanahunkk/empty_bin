import string
import pandas as pd
import config
import time


def get_zone_number(input_record, criteria_id, df_empty_bins, search_times):
    df_zone_number = pd.DataFrame()
    df_devan_height = pd.DataFrame()
    df_devan_height_add = pd.DataFrame()

    # print(f"df_empty_bins \n {df_empty_bins}")
    # df_empty_bins.to_csv("df_empty_bins_before_search_zone.csv", index=False)
    # print(f"input_record:{input_record}")
    # print(f"criteria_id:{criteria_id}")

    df_devan_height = get_devan_height(input_record, criteria_id, df_empty_bins, search_times)
    count_empty = len(df_devan_height)
    # print(f"count_empty(initial):{count_empty}")


    zone_alpha_flag = 0
    if count_empty == 0:
        df_zone_number = change_zone_number(input_record, criteria_id, df_empty_bins, search_times, zone_alpha_flag)
        count_empty = len(df_zone_number)
        # print(f"count_empty(start):{count_empty}")

        if count_empty < config.MAX_EMPTY_BINS:
            zone_alphas = change_zone_alpha(criteria_id.zone_alpha)

            # print(f"zone_alphas{zone_alphas}")
            zone_alpha_flag = 0

            for zone_a in zone_alphas:
                if zone_a == criteria_id.zone_alpha:
                    continue


                if criteria_id.zone_num >= criteria_id.mid_zone_num:
                    alternate_criteria_id = criteria_id._replace(
                        zone_alpha=zone_a,
                        zone_num=criteria_id.max_zone_num,
                        devan_height=1
                    )
                    zone_alpha_flag = 2
                else:
                    alternate_criteria_id = criteria_id._replace(
                        zone_alpha=zone_a,
                        zone_num=criteria_id.start_zone_num,
                        devan_height=1
                    )
                    zone_alpha_flag = 1

                df_zone_number = change_zone_number(input_record, alternate_criteria_id, df_empty_bins, search_times, zone_alpha_flag)
                count_empty = len(df_zone_number)

                # df_devan_height_add = get_devan_height(
                #     input_record, alternate_criteria_id, df_empty_bins, bin_origin
                # )
                #
                # df_devan_height = pd.concat([df_devan_height, df_devan_height_add], ignore_index=True)
                # count_empty = len(df_devan_height)

                if count_empty >= config.MAX_EMPTY_BINS:
                    break
    # print(f"count_empty(final):{count_empty}")
    return count_empty


def get_devan_height(input_record, criteria_id, df_empty_bins, search_times) -> int:
    '''
    Get devan height
    :param input_record:
    :param criteria_id:
    :param df_empty_bins:
    :param search_times:
    :return:
    empty_flag ==   1 : available
                    0 : unavailable
                    2 : tentative
    '''

    # stock_list = StockList()
    # df_stock_list = stock_list.df
    # df_items = item_standard(df_stock_list)
    #
    # tfc_code = input_record.get("Tfc Code")
    # match = df_items.loc[df_items["ITEM CODE"] == tfc_code, "heavy_flag"]
    #
    # if not match.empty:
    #     heavy_flag = match.iloc[0]
    # else:
    #     heavy_flag = None
    #
    # if heavy_flag == 1:
    #     max_height = MAX_HEIGHT_HEAVY
    # else:
    if input_record["heavy_flag"] == 1:
        max_height = config.MAX_HEIGHT_HEAVY
    else:
        max_height = config.MAX_HEIGHT

    if search_times == 1:
        pallet_val = str(input_record.get("Palllet#"))
        has_ref = "ref" in pallet_val.lower()

        criteria_condition = True if has_ref else (df_empty_bins["criteria_id"] == 0)

        filtered_df = df_empty_bins[
            df_empty_bins["bin_number"].str.startswith(criteria_id.location, na=False) &
            df_empty_bins["bin_number"].str.contains(f"-{criteria_id.zone}-", na=False) &
            (df_empty_bins["empty_flag"] == 1) & criteria_condition
        ].copy()

        filtered_df["devan_height"] = (
            filtered_df["bin_number"]
            .str.extract(r"-(\d+)$")
            .astype(int)
        )

        df_equal = filtered_df[filtered_df["devan_height"] == int(criteria_id.devan_height)]
        df_smaller = filtered_df[filtered_df["devan_height"] < int(criteria_id.devan_height)].sort_values(
            by="devan_height", ascending=False
        )
        df_larger = filtered_df[filtered_df["devan_height"] > int(criteria_id.devan_height)].sort_values(
            by="devan_height", ascending=True
        )

        df_devan_height = pd.concat([df_equal, df_smaller, df_larger], ignore_index=True)

        df_devan_height["devan_height"] = df_devan_height["bin_number"].str.extract(r"-(\d+)$").astype(int)
        df_limited = df_devan_height[df_devan_height["devan_height"] <= max_height].reset_index(drop=True)

        # print(f"df_limited1:{df_limited}")

        # print(f"input record \n"
        #       f"{input_record}")
        #
        # print(f"df_devan_heigh VS df_limited \n"
        #       f"{df_devan_height} \n"
        #       f"{df_limited}")
        # if len(df_limited) >= 1:
        #     print(f"df_limited{df_limited}")

        position = 0

        # if len(df_devan_height) >= 1:
        #     target_bin = df_devan_height.iloc[position]["bin_number"]

        if len(df_limited) >= 1:
            target_bin = df_limited.iloc[position]["bin_number"]

            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "empty_flag"] = 0
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "Tfc Code"] = str(input_record.get('Tfc Code'))
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "Palllet#"] = str(input_record.get('Palllet#'))
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "Preferred Bin"] = str(
                input_record.get('Preferred Bin'))
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "Qt"] = input_record.get('Qt')
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "PO name"] = input_record.get('PO name')
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "Target Bin1"] = \
                df_limited["bin_number"].tolist()[0]
            # df_devan_height["bin_number"].tolist()[0]

            print(f"df_devan_height:{df_devan_height["bin_number"].tolist()[0]}")

            # updated_row = df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin]
            # print(updated_row.to_string(index=False))
    else:
        filtered_df = df_empty_bins[
            df_empty_bins["bin_number"].str.startswith(criteria_id.location, na=False) &
            df_empty_bins["bin_number"].str.contains(f"-{criteria_id.zone}-", na=False) &
            (df_empty_bins["empty_flag"] == 1)
            ].copy()

        filtered_df["devan_height"] = (
            filtered_df["bin_number"]
            .str.extract(r"-(\d+)$")
            .astype(int)
        )

        df_equal = filtered_df[filtered_df["devan_height"] == int(criteria_id.devan_height)]
        df_smaller = filtered_df[filtered_df["devan_height"] < int(criteria_id.devan_height)].sort_values(
            by="devan_height", ascending=False
        )
        df_larger = filtered_df[filtered_df["devan_height"] > int(criteria_id.devan_height)].sort_values(
            by="devan_height", ascending=True
        )

        df_devan_height = pd.concat([df_equal, df_smaller, df_larger], ignore_index=True)

        df_devan_height["devan_height"] = df_devan_height["bin_number"].str.extract(r"-(\d+)$").astype(int)
        df_limited = df_devan_height[df_devan_height["devan_height"] <= max_height].reset_index(drop=True)
        # print(f"df_devan_heigh VS df_limited \n"
        #       f"{df_devan_height} \n"
        #       f"{df_limited}")
        # if len(df_limited) >= 1:
        #     print(f"df_limited{df_limited}")

        position = 0

        if len(df_limited) >= 1:
            target_bin = df_limited.iloc[position]["bin_number"]

            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "empty_flag"] = 2
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "Tfc Code"] = str(input_record.get('Tfc Code'))
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "Palllet#"] = str(input_record.get('Palllet#'))
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "Preferred Bin"] = str(
                input_record.get('Preferred Bin'))
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "Qt"] = input_record.get('Qt')
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "PO name"] = input_record.get('PO name')
            df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin, "Target Bin2"] = \
                df_limited["bin_number"].tolist()[0]

            print(f"df_devan_height:{df_devan_height["bin_number"].tolist()[0]}")

            updated_row = df_empty_bins.loc[df_empty_bins["bin_number"] == target_bin]

    # return df_devan_height
    return df_limited


def change_zone_number(input_record, criteria_id, df_empty_bins, search_times, zone_alpha_flag) -> int:
    # print(f"inside change_zone_number")
    from class_bin import BinID
    df_zone_number = pd.DataFrame()

    phase = 1

    if zone_alpha_flag == 1:
        # print(f"inside change_zone_number-1")
        next_zone_num = criteria_id.zone_num
        while True:
            # print(f"next_zone{next_zone_num}")
            # time.sleep(1)
            next_calculated = False
            next_flag = 0
            # criteria_id.zone_num += 1

            if next_zone_num < 0:
                continue
            next_bin = \
                (f"{criteria_id.location}-"
                 f"{criteria_id.zone_alpha}{next_zone_num:02d}-"
                 f"{criteria_id.devan_height}")
            next_bin_id = BinID(next_bin)
            if next_zone_num > next_bin_id.max_zone_num:
                continue

            df_devan_height = get_devan_height(input_record, next_bin_id, df_empty_bins, search_times)
            df_zone_number = pd.concat([df_zone_number, df_devan_height], ignore_index=True)

            if len(df_zone_number) > 0:
                next_flag = 1
                break
            next_calculated = True
            next_zone_num += 1

            # if len(df_zone_number) > 0 or not next_calculated or next_zone_num > 23:
            if (len(df_zone_number) < 0 or
                    not next_calculated or
                    next_zone_num < 0 or
                    next_zone_num > next_bin_id.max_zone_num
            ):
                # print(f"✅ Loop finished.(phase count:{phase})")
                break

    elif zone_alpha_flag == 2:
        print(f"inside change_zone_number-2")
        next_zone_num = criteria_id.zone_num
        while True:
            # print(f"next_zone{next_zone_num}")
            # time.sleep(1)
            next_calculated = False
            next_flag = 0
            # criteria_id.zone_num += 1

            if next_zone_num < 0:
                continue
            next_bin = \
                (f"{criteria_id.location}-"
                 f"{criteria_id.zone_alpha}{next_zone_num:02d}-"
                 f"{criteria_id.devan_height}")
            next_bin_id = BinID(next_bin)
            if next_zone_num > next_bin_id.max_zone_num:
                continue

            df_devan_height = get_devan_height(input_record, next_bin_id, df_empty_bins, search_times)
            df_zone_number = pd.concat([df_zone_number, df_devan_height], ignore_index=True)

            if len(df_zone_number) > 0:
                next_flag = 1
                break
            next_calculated = True
            next_zone_num -= 1
            # if len(df_zone_number) > 0 or not next_calculated or next_zone_num > 23:
            if (len(df_zone_number) < 0 or
                    not next_calculated or
                    next_zone_num < 0 or
                    next_zone_num > next_bin_id.max_zone_num
            ):
                # print(f"✅ Loop finished.(phase count:{phase})")
                break
    else:
        while True:
            next_calculated = False
            next_flag = 0
            for direction in [-1, 1]:
                next_zone_num = criteria_id.zone_num + (2 * phase * direction)
                if next_zone_num < 0:
                    continue

                next_bin = \
                    (f"{criteria_id.location}-"
                     f"{criteria_id.zone_alpha}{next_zone_num:02d}-"
                     f"{criteria_id.devan_height}")
                next_bin_id = BinID(next_bin)

                if next_zone_num > next_bin_id.max_zone_num:
                    continue

                # print(f" --- next_bin_id: {next_bin_id}")

                df_devan_height = get_devan_height(input_record, next_bin_id, df_empty_bins, search_times)
                df_zone_number = pd.concat([df_zone_number, df_devan_height], ignore_index=True)

                # print(f"df_zone_number(next) : {df_zone_number}")
                if len(df_zone_number) > 0:
                    next_flag = 1
                    break

                next_calculated = True

            # exit(0)
            if phase > 3 & next_flag == 0:
                for direction2 in [-1, 1]:
                    back_zone_num = criteria_id.zone_num + (2 * (phase - 3) - 1) * direction2

                    if back_zone_num < 0:
                        continue

                    back_bin = \
                        (f"{criteria_id.location}-"
                         f"{criteria_id.zone_alpha}{back_zone_num:02d}-"
                         f"{criteria_id.devan_height}")
                    back_bin_id = BinID(back_bin)

                    if back_zone_num > back_bin_id.max_zone_num:
                        continue

                    # print(f" === back_bin_id: {back_bin_id}")

                    df_devan_height = get_devan_height(input_record, back_bin_id, df_empty_bins, search_times)
                    df_zone_number = pd.concat([df_zone_number, df_devan_height], ignore_index=True)
                    # print(f"df_zone_number(back) : {df_zone_number}")
                    if len(df_zone_number) > 0:
                        break
                    # count_back = len(df_devan_height_total)
                    # count_total += count_back

                    next_calculated = True

            phase += 1

            if len(df_zone_number) > 0 or not next_calculated or phase > config.PHASE_MAX :
            #     # print(f"✅ Loop finished.(phase count:{phase})")
                break

    return df_zone_number
    # return count_total


def change_zone_alpha(zone_alpha: str) -> list[str]:
    letters = list(string.ascii_uppercase[:9])  # ['A','B','C','D','E','F','G','H','I']

    if zone_alpha.upper() not in letters:
        raise ValueError(f"'{zone_alpha}' is out of range (A~I only).")

    idx = letters.index(zone_alpha.upper())
    result = [letters[idx]]

    left = idx - 1
    right = idx + 1
    toggle = True

    while left >= 0 or right < len(letters):
        if toggle and left >= 0:
            result.append(letters[left])
            left -= 1
        elif not toggle and right < len(letters):
            result.append(letters[right])
            right += 1
        toggle = not toggle

    return result