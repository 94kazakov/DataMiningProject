'''
myBayesian
'''
from bayesian.bbn import build_bbn
import csv

drug_prob = {}

def get_probs(my_file):
  '''
  Extract the data from the given CSV file, then 
  calculate probabilities.

  my_file - A CSV file with the column format
            [drugs,reaction]
  '''
  data = []
  ## Read data
  f1 = open(my_file, 'rt')
  try:
    reader = csv.reader(f1)
    ## skip first line
    next(reader)
    for row in reader:
      data.append(row)

  finally:
    f1.close()

  ## Test data, remove later
  #data = [['D1;D2;D3', 'R1'],['D2','R2:R3']]

  ## Do Work
  drug_count = {}
  global drug_prob
  total_reports = len(data)
  for report in data:
    drugs = report[0].split(';')
    reactions = report[1].split(';')

    ## Count the number of occurrences for each drug.
    ## This assumes the same drug is not listed  
    ## more than once in the same report...
    for drug in drugs:
      if drug not in drug_count:
        drug_count[drug] = 1
      else:
        drug_count[drug] = drug_count[drug] + 1

    ## If drug X is present, what is the probability 
    ## Effect Y is present as well?
    for reaction in reactions:
      pass


  for drug in drug_count:
    drug_prob[drug] = float(drug_count[drug])/float(total_reports)

  #print drug_prob



  #return drug_prob,'Undefined'



def f_drugs(drug):
  '''
  Need frequency of each drug appears
  '''
  global drug_prob
  if drug in drug_prob:
    #print drug, drug_prob[drug]
    return drug_prob[drug]
  else:
    print 0
    return 0


def f_reactions(drug, reaction):
  '''
  Need frequency of a reaction appears based on the drugs
  '''
  #print 'react'
  return 1


if __name__=='__main__':
  #global drug_prob
  get_probs('openFDA_data2.csv')
  g = build_bbn(
    f_drugs,
    f_reactions,
    domains=dict(
      drug=list(drug_prob)[:5],
      reaction=list(drug_prob)[6:10]))
  g.q()
