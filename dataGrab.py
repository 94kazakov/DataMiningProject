#!/usr/bin/env python
import urllib2
import json

def getQuery(q):
    apiKey = 'WNMUZqIPTWehl4IdmDlcE6ft2Q9t9AImq2d7j6pR'
    url = 'https://api.fda.gov/drug/event.json?api_key=' + apiKey + '&search=receivedate:[20040101+TO+20081231]&limit=100'
    json_obj = urllib2.urlopen(url)
    data = json.load(json_obj) 

    for item in data['results']:
        for key in item['patient']['reaction']:
            print "reaction is: " + str(key['reactionmeddrapt'])

#queryGen = 'https://api.fda.gov/drug/event.json?'
#q = 'https://api.fda.gov/drug/event.json?search=receivedate:[20040101+TO+20081231]&limit=100'
#getQuery(q)


def getData(num_results):
    '''
    !!! getData_try is a better function to use !!!    
    
    Requests the given number of reports, grabs the desired data points,
    and stores them in a list
    '''
    apiKey = 'WNMUZqIPTWehl4IdmDlcE6ft2Q9t9AImq2d7j6pR'
    url = 'https://api.fda.gov/drug/event.json?api_key=' + apiKey + '&search=receivedate:[20040101+TO+20081231]&limit=' + str(num_results)
    json_obj = urllib2.urlopen(url)
    data = json.load(json_obj)
    results = []    
    
    for item in data['results']:
        ## Header info
        report_id = item['safetyreportid']
        #serious = item['serious']  # 1 = yes, 2 = no
        #country = item['occurcountry']  # broken
        if item['receiptdateformat'] == '102':
            date = item['receiptdate']
            date = date[4:6]+'/'+date[6:8]+'/'+date[0:4]
        else:
            date = None
        
        
        ## Patient info
        patient = item['patient']
        if 'age' in patient:
            age = patient['patientonsetage'] # not always year, could fix
        else:
            age = None
        #weight = patient['patientweight']  # broken            
        
        if 'sex' in patient:
            sex = patient['patientsex']
            if sex == '2':
                sex = "Female"
            elif sex == '1':
                sex = "Male"
        else:
            sex = None
            

            
        ## Drug info
        drug_list = []
        for drug in patient['drug']:
            if 'drugcharacterization' in drug:
                role = drug['drugcharacterization']
                if role == '1':
                    role = 'Suspect'
                elif role == '2':
                    role = 'Concomitant'
                elif role == '3':
                    role = 'Interacting'
            else:
                role = None
            
            if 'openfda' in drug: 
                openFDA = drug['openfda']
                if 'brand_name' in openFDA:
                    brand_name = openFDA['brand_name'] # list
                elif 'medicinalproduct' in drug:
                    brand_name =  drug['medicinalproduct']
                else:
                    brand_name = None
                    
                if 'generic_name' in openFDA:
                    gen_name = openFDA['generic_name'] # list
                else:
                    gen_name = None

                if 'substance_name' in openFDA:
                    substance = openFDA['substance_name'] # list
                else:
                    substance = None

                #product_type?
                #route?
                #spl stuff?
                
            else:
                if 'medicinalproduct' in drug:
                    brand_name =  drug['medicinalproduct']
                else:
                    brand_name = None                
                gen_name = None
                substance = None
            if brand_name != None:
                drug_list.append({'brand_name':brand_name, 'gen_name':gen_name, 'substance':substance})
        
        ## Reaction info
        reactions = []
        for reaction in patient['reaction']:
            reactions.append(reaction['reactionmeddrapt'])
        
        ## list of data 
        print report_id, date, age, sex, role, brand_name, gen_name, substance, reactions
        
        results.append({'report_id':report_id, 'date':date, 'age':age, 
                        'sex':sex, 'drugs':drug_list, 'reactions':reactions})
    return results

#tmp = getData(100)


def getData_try(num_results):
    '''
    DIFFERENCE: one large try catch statement that filters out results with 
    missing points. Can handle more than 100 requests
    
    Requests the given number of reports, grabs the desired data points,
    and stores them in a list of dictionaries
    
    num_results - the number of entries you want to pull
    '''
    ## Variables
    results = []  ## list of data to be returned        
    apiKey = 'WNMUZqIPTWehl4IdmDlcE6ft2Q9t9AImq2d7j6pR'  ## our key for openFDA
    skips = 0 ## a counter for pulling more than the 100 results allowed per query
    
    ## Query the openFDA database and strip out the data we want    
    while num_results > 0:
        url = 'https://api.fda.gov/drug/event.json?api_key=' + apiKey + '&search=receivedate:[20040101+TO+20081231]'

        ## Set the number of results pulled 
        if num_results < 100:
            search_lim = num_results
        else:
            search_lim = 100
        num_results = num_results - search_lim
        
        ## Add the wanted limit and skip parameters for this round to the query
        url = url + '&limit=' + str(search_lim) + '&skip=' + str(skips)
        skips = skips + search_lim
        
        ## Make the query to OpenFDA
        json_obj = urllib2.urlopen(url)
        data = json.load(json_obj)    
        
        ## Loop through the data and attempt to strip out the fields we desire.
        ## If a field doesn't exist, skip the whole item and don't add it to 
        ## the final results
        for item in data['results']:
            try:
                ## Header info
                report_id = item['safetyreportid']
               
                if item['receiptdateformat'] == '102':
                    date = item['receiptdate']
                    date = date[4:6]+'/'+date[6:8]+'/'+date[0:4]
                else:
                    date = None
                
                ## Patient info
                patient = item['patient']
                    
                ## Drug info
                drug_list = []
                for drug in patient['drug']:
                    '''
                    role = drug['drugcharacterization']
                    if role == '1':
                        role = 'Suspect'
                    elif role == '2':
                        role = 'Concomitant'
                    elif role == '3':
                        role = 'Interacting'
                    '''
                    ## OpenFDA field in the drug field
                    openFDA = drug['openfda']
                    substance = openFDA['substance_name']
                    '''                    
                    try:                
                        openFDA = drug['openfda']
                        #brand_name = openFDA['brand_name']
                        #gen_name = openFDA['generic_name']
                        substance = openFDA['substance_name']
                        #product_type?
                        #route?
                        #spl stuff?
                    except KeyError:
                        if 'medicinalproduct' in drug:
                            brand_name = drug['medicinalproduct']
                            gen_name = None
                            substance = None
                        else:
                            brand_name = None                        
                            gen_name = None
                            substance = None 
                    '''
                    ## Add the drug info to the list to be returned
                    drug_list.append({'substance':substance})
                    #drug_list.append({'brand_name':brand_name, 'gen_name':gen_name, 'substance':substance})
                
                ## Reaction info
                reactions = []
                for reaction in patient['reaction']:
                    ## Add the reactions to the list to be returned
                    reactions.append(reaction['reactionmeddrapt'])
                        
                ## Add the info from the current report item to the results 
                ## list. Format this to change the data returned
                ############################################################
                results.append({'report_id':report_id, 'date':date,
                                'drugs':drug_list, 'reactions':reactions})

            except KeyError:
                ## Missing vital data field, skipping item
                pass    
        
    print "Number of complete results: ",len(results)
    #print results
    return results       
    
    
#data = getData_try(6)


def format_data(num_results):
    '''
    A wrapper function. Takes the data from the data retrieval function and 
    changes it to the desired format.
    
    num_results - the number of entries you want to pull
    '''
    data = getData_try(num_results)
    results = []
    for item in data:
        drugs = []
        for drug in item['drugs']:
            for substance in drug['substance']:
                drugs.append(substance)
        results.append({'drugs':drugs, 'reactions':item['reactions']})
    
    return results

#data = format_data(10)

def format_data_1react(num_results):
    '''
    A wrapper function. Takes the data from the data retrieval function and 
    changes it to the desired format. In this case, that is a list of drugs 
    being used by a patient for each of their reactions
    
    num_results - the number of entries you want to pull
    '''
    data = getData_try(num_results)
    results = []
    for item in data:
        drugs = []
        for drug in item['drugs']:
            for substance in drug['substance']:
                if substance not in drugs:
                    drugs.append(substance)
        for reaction in item['reactions']:
            results.append({'drugs':drugs, 'reactions':reaction})
    
    return results

#data = format_data_1react(10)
#print data

def toCSV(my_file, num_results):
    '''
    Creates a CSV file and populates it with data pulled from the openFDA site

    my_file - name of the CSV file you want to make
    num_results - the number of entries you want to pull
    
    NOTE: currently, only about 1/5 of the data pulled from the site has the 
    data fields we need
    '''
    ## Get the data
    data = format_data(num_results)    
    
    ## Open the CSV file to write to
    f = open(my_file, 'w')
    
    ## Write data titles to file
    f.write('drugs,reactions\n')
    
    for item in data:
        drug_list = ''
        reaction_list = ''
        for drug in item['drugs']:
            drug_list = drug_list+drug+";"
        for reaction in item['reactions']:
            reaction_list = reaction_list+reaction+";"
    
        ## Remove the last semicolon
        drug_list = drug_list[:len(drug_list)-1]
        reaction_list = reaction_list[:len(reaction_list)-1]
        
        ## Write the data to the file
        f.write(drug_list+","+reaction_list+"\n")

    ## Close the file
    f.close()
        
#toCSV("openFDA_data.csv", 5000)
