# -*- coding: utf-8 -*-

import infermedica_api

#parse through user description for symptoms
def parser(api, userSymptoms):
    response = api.parse(userSymptoms)
    possibleSympt = response.mentions
    return possibleSympt

#add symptoms to request
def addSympt(request, sympt):
    for i in sympt:
        if i ==sympt[0]:
            request.add_symptom(i.id,i.choice_id,initial = True)
        request.add_symptom(i.id,i.choice_id)

#Parameters are api, (sex,age), user symptoms after parse
def diagnose(api, patientBasic, sympt):
    request = infermedica_api.Diagnosis(sex = patientBasic[0],age = patientBasic[1])
    addSympt(request, sympt)
    request = api.diagnosis(request)
    return request

#returns a list of the 3 most probable conditions based on diagnosis 
def conditions(request):
    cond = request.conditions[:3]
    condNames = []
    for i in range(3):
        condNames.append(cond[i]["name"])
    return condNames
        
#User Response is a list of tuples with (s_id,response)
#def questionHandler(request,userResponse):

def main():
    api= infermedica_api.API(app_id='52457f85', app_key='95f03f5398a3b0358795540117d4f376')
    #user answers question
    request = diagnose(api,("female","35"),parser(api,'i feel smoach pain but no couoghing today'))
    #returns list of top 3 most probable conditions
    print(conditions(request))
    
main()
    
    
    
    
    
    
    
    
    