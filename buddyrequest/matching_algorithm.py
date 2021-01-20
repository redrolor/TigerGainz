import pandas as pd
from fuzzywuzzy import fuzz
from statistics import mean
import pytz_convert as pc

def Keys_from_values(dict,value):
    for item in dict.values():
        if item == value:
            value_list = list(dict.values())
            indexer = value_list.index(value)
            key_list = list(dict.keys())
            ret_val = key_list[indexer]

    return ret_val


def dict_creator(key, value):  # makes dictionary from two lists containing the list of keys and list of values
    dictionary = {}
    for item in key:
        dictionary[item] = value[key.index(item)]
    return dictionary


def get_matches(user_data_list, requests_list):


    pd.set_option("display.max_rows", None, "display.max_columns", None) # makes printing out of large dataframes easier

    #############################################STEP 1: DATAFRAME CREATION#############################################
    requestsdf = pd.DataFrame(requests_list) # converts requests list into a dataframe

    # gets relevant information from requests dataframe
    names = requestsdf.loc[:,'name'].tolist()
    net_id = requestsdf.loc[:, "netID"].tolist()
    id_list = requestsdf.loc[:, "id"].tolist()

    # creating a list of tuples containing the name and netID of each entry in the request database
    name_netID = []

    for entry in range(len(names)):
        h = (names[entry], net_id[entry])
        name_netID.append(h)


    preferences = user_data_list[0] # is a list of how the user ranks each of the workout matching factors
    Dfuser = pd.DataFrame({"days": [user_data_list[1]], "duration": [user_data_list[2]], "workout_type": [user_data_list[3]], "time_zone": [user_data_list[4]]})
    print(Dfuser)
    Dfrq = requestsdf


    Dfrq1 = Dfrq.drop(columns = ['name', 'id','netID','rescollege','major','year','user_id','partner_id'])


    #Mock priorities dictionary [PLACE HOLDER]
    priorities = {"days":preferences[1] ,"duration": preferences[2], "time_zone":preferences[0]}
    reference_ranker = {1: 100, 2: 60, 3: 50}

    '''At the end of step 1, two dataframes are created. Dfrq1: a dataframe for all existing users already in the database
    and Dfuser: a dataframe with one row that contains all the matching preferences of the user trying to make a match.
    '''

    ################################################STEP 2: MATCHING###################################################

    # following code guarantees that all workout users will have the same workout type regardless of other preferences
    workout = Dfuser.iloc[0]["workout_type"] # isolates the workout type -- should be a string

    matching_df_request = pd.DataFrame({}) # creating a new empty dataframe for people that have the same workout type
    Dfrq_row_list = [] # empty list for for all the index of the user in the request database

    # for loop guarantees match has same type of workout and adds users with the same workout to matching_df_request
    for index_row in range(len(Dfrq1)):
        if fuzz.ratio(workout, Dfrq1.iloc[index_row]["workout_type"]) == 100:
            row = Dfrq1.iloc[index_row]
            matching_df_request = matching_df_request.append(row) #this is the dataframe that we will be comparting with Dfuser to find the
                                                                    #actualy matches
            Dfrq_row_list.append(index_row) # appends that user's row index to Dfrq_row_list

    matching_df_request["Dfrq_index"] = Dfrq_row_list

    if len(matching_df_request) > 0: # if we have users in the new dataframe we can drop workouts as a matching parameter
                                    # since we already matched based on workouts.

        matching_df_user = Dfuser.drop("workout_type", axis=1)
        matching_df_request = matching_df_request.drop("workout_type", axis=1)
        column_labels = matching_df_request.columns.tolist()

    else: # break and return a blank array back to views
        blankarray=[]
        return blankarray
        print("return to home screen")


    '''
    Following code matches of the rest of the parameters. Using a double for loop, it goes through every column (workout factor) of
    every row (user in the matching dataframe) and compares each factor to the entry in the user dataframe. Regardless of
    matching parameter here are a few variables to keep in mind:

    rel_val = how good a match is for that specific parameter. e.g. a rel_val of 100 in "days" would indicate a perfect match
              for days.

    ranker = the priority that user gives to that factor. e.g ranker = 1 for days would indicate the user trying to match
    gives weights days the most important.

    For every rank there is a set cut_off for the minimum best match score for the
    respective workout factor. This cut_off is stored in a dictionary.
    '''
    ListOfMatches = [] # array where all suitable matches will be appended to later
    for row in range(len(matching_df_request)):
        list_best_match_vals = [] # for every user we generate an array
        for column in range(len(column_labels)):


            if column_labels[column] == "days":
                rel_val = fuzz.partial_token_sort_ratio(matching_df_request.iloc[row][column], matching_df_user.iloc[0][column])
                ranker = priorities.get(column_labels[column])
                cut_off = reference_ranker.get(ranker)

                weighted_average = (cut_off/100) * rel_val

                if rel_val >= cut_off: # if minimum score is not met, we discard the prospective match completely
                    list_best_match_vals.append(weighted_average)
                else:
                    break

            elif column_labels[column] == "duration":
                ranker = priorities.get(column_labels[column]) #gets the priority of duration
                window = (ranker - 1)(30) #calculates a window of acceptable time e.g. 60 minutes can still be matched with 90 mins

                if int(matching_df_request.iloc[row][column]) - window <= int(matching_df_user.iloc[0][column]) \
                        <= int(matching_df_request.iloc[row][column]) + window:

                    rel_val = 100 #set match equal to

                    ranker = priorities.get(column_labels[column])
                    cut_off = reference_ranker.get(ranker)

                    weighted_average = (cut_off / 100) * rel_val
                    list_best_match_vals.append(weighted_average)

                else:
                    break

            elif column_labels[column] == "time_zone":
                ranker = priorities.get(column_labels[column])  # gets the priority of time zone --> also determines the window of error allowed for time zone
                                                                # e.g. a person who ranks timezone as their #1 priority would match with ppl +/- 1 hour

                user_time_zone = matching_df_user.iloc[0][column]
                request_time_zone = atching_df_request.iloc[row][column]

                difference = abs(user_time_zone - request_time_zone)

                if difference <= ranker:
                    cut_off = reference_ranker.get(ranker)

                    weighted_average = (cut_off / 100) * rel_val
                    list_best_match_vals.append(weighted_average)

                else:
                    break

            else:

                rel_val = fuzz.partial_ratio(matching_df_request.iloc[row][column],
                                                        matching_df_user.iloc[0][column])

                weighted_average = 50

                if rel_val >= cut_off:  # if minimum score is not met, we discard the prospective match completely
                    list_best_match_vals.append(weighted_average)

                else:
                    break



        if len(list_best_match_vals) == len(column_labels) - 1: #if every single column managed to pass the cut_off val
            average = mean(list_best_match_vals)
            list_best_match_vals.append(average)
            Dfrq_index = matching_df_request.iloc[row]["Dfrq_index"]
            list_best_match_vals.append(Dfrq_index)
            ListOfMatches.append(list_best_match_vals) #last element of each sublist is the index of that row in the database


        #ListOfMatches is a nested list containing

    n = 0
    while n < len(ListOfMatches): #will stop the loop when we have looped through n-1 times
        n += 1 #counter that ensures we are below n
        for i in list(range(len(ListOfMatches) - 1)): #for every index value in list of index values
          if ListOfMatches[i][-2] < ListOfMatches[i+1][-2]: #Conditional statement that compares if i and its adjacent value
                                                            #-2 ensures that the sorting is based on the final weighted average
                                                            #for each row
            ListOfMatches[i], ListOfMatches[i+1] = ListOfMatches[i+1], ListOfMatches[i] #swaps if adjacent value is smaller


    row_index = []
    for entry in ListOfMatches:
        val = entry[-1]
        row_index.append(val)

    presentation_list = []
    for index in row_index:
        row = Dfrq.iloc[index].tolist()
        presentation_list.append(row)

    return presentation_list
