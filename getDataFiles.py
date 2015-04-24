# -*- coding: utf-8 -*-
"""
getDataFiles.py
"""
from dataGrab import toCSV
import os


def combine_files(files):
    '''
    Combines the given array of files into 1 file
    
    files - an array of strings
    '''
    ## The local path to the files
    path = "C:/Users/Tyler/Documents/college/Data Mining/" 

    with open(path+'openFDA_data_all.csv', 'w') as outfile:
        outfile.write('drugs,reactions,id,date,sex,age\n')
        for fname in files:
            with open(fname) as infile:
                for line in infile:
                    if line != 'drugs,reactions,id,date,sex,age\n':
                        outfile.write(line)
            os.remove(fname)


def get_data_in_mass(file_size, num_files, num_skip):
    '''
    Creates a given number of files with a given maximum 
    number of reports in each, skipping the first number
    of reports equal to num_skip
    
    file_size - the maximum number of reports per file
    num_files - the number of files to make
    num_skips - the initial number of reports to skip
    '''
    ## The local path to the files
    path = "C:/Users/Tyler/Documents/college/Data Mining/" 
    
    print "Creating files..."
    curr_skip = num_skip
    files = []
    for index in range(num_files):
        curr_file = path+"openFDA_data"+str(index)+".csv"
        files.append(curr_file)
        toCSV(curr_file, file_size, curr_skip)
        curr_skip += file_size
        print "  File",index,"of",num_files,"complete"

    print "Combining files..."    
    combine_files(files)
    


## Limit 240 requests/minute,  120000 requests/ day
if __name__ == "__main__":
    #get_data_in_mass(10000,20,1267000)
    
    path = "C:/Users/Tyler/Documents/college/Data Mining/" 
    #files = [path+'openFDA_data_all1.csv',path+'openFDA_data_all2.csv']    
    #combine_files(files)   
    '''
    files = [path+'openFDA_data_all1.csv']
    for i in range(0,15):
        files.append(path+'openFDA_data'+str(i)+'.csv')
    combine_files(files)   
    '''
