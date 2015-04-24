#!/usr/bin/env python
import urllib2
import json
import rxlist

def getQuery(q):
    apiKey = 'WNMUZqIPTWehl4IdmDlcE6ft2Q9t9AImq2d7j6pR'
    url = 'https://api.fda.gov/drug/event.json?api_key=' + apiKey + '&search=receivedate:[20040101+TO+20081231]&limit=100'
    json_obj = urllib2.urlopen(url)
    data = json.load(json_obj) 

    for item in data['results']:
        for key in item['patient']['reaction']:
            print "reaction is: " + str(key['reactionmeddrapt'])


def getData_try(num_results, skip_offset):
    '''
    Requests the given number of reports, grabs the desired data points,
    and stores them in a list of dictionaries
    
    num_results - the number of entries you want to pull
    skip_offset - the initial number of reports to skip
    '''
    ## Variables
    results = []  ## list of data to be returned        
    apiKey = 'WNMUZqIPTWehl4IdmDlcE6ft2Q9t9AImq2d7j6pR'  ## our key for openFDA
    skips = skip_offset ## a counter for pulling more than the 100 results allowed per query
    
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
                age = patient['patientonsetage'] 
                age_unit = patient['patientonsetageunit']
                if age_unit == '800':
                    age = unicode(float(age)*10.0)  ## Age in Decades 
                elif age_unit == '801':
                    pass  ## Age in Years
                elif age_unit == '802':
                    age = unicode(float(age)/12.0)  ## Age in Months 
                elif age_unit == '803':
                    age = unicode(float(age)/52.0)  ## Age in Weeks
                elif age_unit == '804':
                    age = unicode(float(age)/365.0)  ## Age in Days 
                elif age_unit == '805':
                    age = unicode(float(age)/8760.0)  ## Age in Hours

                sex = patient['patientsex']
                if sex == '2':
                    sex = "Female"
                elif sex == '1':
                    sex = "Male"
                else:
                    sex = "None"

                ## Drug info
                drug_list = []
                for drug in patient['drug']:                    
                    try:
                        ## OpenFDA field in the drug field
                        openFDA = drug['openfda']
                        brand_name = openFDA['brand_name']
                        #substance = openFDA['substance_name']
                    except KeyError:
                        brand_name = [drug['medicinalproduct']]
                        

                    ## Add the drug info to the list to be returned
                    drug_list.append({'brand_name':brand_name})
                    #drug_list.append({'substance':substance})
                    #drug_list.append({'brand_name':brand_name, 'gen_name':gen_name, 'substance':substance})
                
                ## Reaction info
                reactions = []
                for reaction in patient['reaction']:
                    ## Add the reactions to the list to be returned
                    reactions.append(reaction['reactionmeddrapt'])

                ## Add the info from the current report item to the results 
                ## list. Format this to change the data returned
                ############################################################
                results.append({'report_id':report_id, 'date':date, 'sex':sex,
                                'age':age,'drugs':drug_list, 'reactions':reactions})

            except KeyError:
                ## Missing vital data field, skipping item
                pass    
    
    print "Number of complete results: ",len(results)
    return results       
    
    

def format_data(num_results, skip_offset):
    '''
    A wrapper function. Takes the data from the data retrieval function and 
    changes it to the desired format.
    
    num_results - the number of entries you want to pull
    skip_offset - the initial number of reports to skip
    '''
    data = getData_try(num_results, skip_offset)
    brand_map = rxlist.map_brandnames()
    results = []
    for item in data:
        drugs = []
        for drug in item['drugs']:
            for brand in drug['brand_name']:
                ## Map the brand name tot the generic name
                generic = rxlist.brand_to_generic(brand_map,brand)
                if generic != None:
                    drugs.append(generic)
                else:
                    
                    drugs.append(brand)
                    
        results.append({'drugs':drugs, 'reactions':item['reactions'], 
                        'sex':item['sex'], 'age':item['age'], 
                        'id':item['report_id'], 'date':item['date']})

    return results



def toCSV(my_file, num_results, skip_offset):
    '''
    Creates a CSV file and populates it with data pulled from the openFDA site

    my_file - name of the CSV file you want to make
    num_results - the number of entries you want to pull
    skip_offset - the initial number of reports to skip
    
    NOTE: currently, only about 4/5 of the data pulled from the site has the 
    data fields we need
    '''
    ## Get the data
    data = format_data(num_results, skip_offset)        
    
    ## Open the CSV file to write to
    f = open(my_file, 'w')
    
    ## Write data titles to file
    f.write('drugs,reactions,id,date,sex,age\n')
    
    for item in data:
        drug_list = []
        reaction_list = []
        
        ## Strip unwanted characters
        for drug in item['drugs']:          
            if type(drug) != None:
                drug = str(drug).replace(',','')
                drug = str(drug).replace(';','')
                drug = str(drug).replace('(','')
                drug = str(drug).replace(')','')
                drug_list.append(drug)                

        for reaction in item['reactions']:
            reaction = str(reaction).replace(',','')
            reaction = str(reaction).replace(';','')
            reaction = str(reaction).replace('(','')
            reaction = str(reaction).replace(')','')
            reaction_list.append(reaction)

        if drug_list != None and len(drug_list) != 0:
            ## Remove duplicates
            drug_list = list(set(drug_list))
            reaction_list = list(set(reaction_list))                      
            
            ## Turn into a string separated by ';'
            drug_list = ';'.join(drug_list)
            reaction_list = ';'.join(reaction_list)
            
            ## Get other attributes
            report_id = item['id']
            date = item['date']        
            sex = item['sex']
            age = item['age']
            
            ## Remove the outliers where the drug list is too long for 
            ## Python to handle
            if len(drug_list) < 30000:  
                ## Write the data to the file
                f.write(drug_list+","+reaction_list+","+report_id+
                        ","+date+","+sex+","+age+"\n")
            
    ## Close the file
    f.close()

