'''
myBayesian
'''
from bayesian.bbn import build_bbn
import csv

drug_prob = {}
react_prob = {}

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
  react_count = {}
  global drug_prob
  global react_prob
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
        if drug not in react_count:
          react_count[drug] = {}
          react_count[drug][reaction] = 1
        else:
          if reaction not in react_count[drug]:
            react_count[drug][reaction] = 1
          else:
            react_count[drug][reaction] = react_count[drug][reaction] + 1


  for drug in drug_count:
    drug_prob[drug] = float(drug_count[drug])/float(total_reports)

  for drug in react_count:
    for reaction in react_count[drug]:
      if drug not in react_prob:
        react_prob[drug] = {}
      react_prob[drug][reaction] = float(react_count[drug][reaction])/float(drug_count[drug])
      print react_prob[drug][reaction], drug, reaction
  #print react_prob['IMIGLUCERASE']
  #return drug_prob



def f_drugs(drug):
  '''
  Need frequency of each drug appears
  '''
  global drug_prob
  if drug in drug_prob:
    return drug_prob[drug]
  else:
    return 0


def f_reactions(drug, reaction):
  '''
  Need frequency of a reaction appears based on the drugs
  '''
  global react_prob
  if drug in react_prob:
    if reaction in react_prob[drug]:
      print 'YES'
      return react_prob[drug][reaction]

  return 0


if __name__=='__main__':
  #global drug_prob
  get_probs('openFDA_data2.csv')
  g = build_bbn(
    f_drugs,
    f_reactions,
    domains=dict(
      drug=list(drug_prob)[:1],
      reaction=list(react_prob)[:1]))
  #g.q()
  g.q(drug='IMIGLUCERASE')

'''
import pystan

schools_code = """
data {
    int<lower=0> J; // number of schools
    real y[J]; // estimated treatment effects
    real<lower=0> sigma[J]; // s.e. of effect estimates
}
parameters {
    real mu;
    real<lower=0> tau;
    real eta[J];
}
transformed parameters {
    real theta[J];
    for (j in 1:J)
    theta[j] <- mu + tau * eta[j];
}
model {
    eta ~ normal(0, 1);
    y ~ normal(theta, sigma);
}
"""

schools_dat = {'J': 8,
               'y': [28,  8, -3,  7, -1,  1, 18, 12],
               'sigma': [15, 10, 16, 11,  9, 11, 10, 18]}

fit = pystan.stan(model_code=schools_code, data=schools_dat,
                  iter=1000, chains=4)


print fit
'''
