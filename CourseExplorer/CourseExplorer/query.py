'''
Created on Jul 10, 2012

@author: hyeokim
'''

import urllib
import httplib2
import json
import rdflib
import rdfalchemy
from django.db import models
from googlemaps import GoogleMaps
from django.utils   import html

repository = 'luci'
endpoint = "http://luci.uwl.ac.uk/openrdf-sesame/repositories/%s" % (repository)
    
LUCI = rdflib.Namespace('http://luci.uwl.ac.uk/course_linkeddata/')
RDF = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
DC = rdflib.Namespace('http://purl.org/dc/elements/1.1/')

breadcrumb = [];

class breadcrumbModel:
    def __init__(self, url, title):
        self.url = url
        self.title = title
        
        
def get_course(title, type):
    query = """PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX luci:<http://luci.uwl.ac.uk/course_linkeddata/> 
    PREFIX dc:<http://purl.org/dc/elements/1.1/> 
    construct { ?course a luci:Course ; dc:title ?courseTitle . } """
    
    if(type == "course"):
        query += "where {?course rdf:type luci:Course ; dc:title ?courseTitle .}"
    if(type == "campus"):
        query += """ where {?course rdf:type luci:Course ;
                                    dc:title ?courseTitle ;
                                    luci:specifies ?offering .
                    ?offering luci:isOfferedAt ?location .
                    ?location dc:title ?locationTitle . 
                     filter(?locationTitle = '%s') }"""  % (title)
    if(type == "school"):
        query += """where {?course rdf:type luci:Course ;
                                    dc:title ?courseTitle ;
                                    luci:specifies ?offering .
                    ?offering luci:school ?school .
                     filter(?school = '%s') }""" % (title)
                     
    print "POSTing SPARQL query to %s" % (endpoint)
    params = { 'query': query }
    headers = { 
      'content-type': 'application/x-www-form-urlencoded', 
      'accept': 'text/plain'  
    }
    (response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
    
    print "Response %s" % response.status
    
    graph = rdflib.ConjunctiveGraph()
    graph.parse(rdflib.parser.StringInputSource(content), format="nt")

    print "Loaded %d triples" % len(graph)

    
    class Course(rdfalchemy.rdfSubject):
        rdf_type = LUCI.Course
        title = rdfalchemy.rdfSingle(DC.title)
    
    rdfalchemy.rdfSubject.db = graph
    
    
    class CourseModel:
        def __init__(self, cid, title):
            self.cid = cid
            self.title = title
    
    course_list = []

    for course in Course.ClassInstances():
        cid = course.resUri
        courseModel = CourseModel(cid[cid.find("#")+1:], course.title)
        course_list.append(courseModel)
    
   
    return course_list

'''   
    for course in Course.ClassInstances():
        print course 
        print course.title
        
        
    class CourseModel(models.Model):
    cid = models.CharField(max_length=128)
    title = models.CharField(max_length=256)

    for course in Course.ClassInstances():
        CourseModel(course.resUri, course.title)
        
    course_list = CourseModel.objects.all() 
'''

def get_courseDetail(course_id):
    
    course_id = "<http://luci.uwl.ac.uk/course_linkeddata/Course#"+course_id+">"
    query = """PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX luci:<http://luci.uwl.ac.uk/course_linkeddata/> 
    PREFIX dc:<http://purl.org/dc/elements/1.1/> 
    construct { ?course a luci:Course ; dc:title ?title ; luci:abstract ?abstract ; dc:subject ?subject ; luci:specifies ?offerings ; 
         dc:description ?description ; luci:qualification ?qualification ; 
        luci:applicationProcedure ?application ; luci:learningOutcome ?learningoutcome . } 
    where { ?course rdf:type luci:Course ; 
                    dc:title ?title . 
        optional { ?course luci:abstract ?abstract .}
        optional { ?course dc:subject ?subject .}
        optional { ?course luci:specifies ?offerings .} 
        optional { ?course dc:description ?description .} 
        optional { ?course luci:qualification ?qualification .} 
        optional { ?course luci:applicationProcedure ?application .} 
        optional { ?course luci:learningOutcome ?learningoutcome . } 
                  
     filter (?course = %s)}""" % (course_id)
     #  } """
     
    print "POSTing SPARQL query to %s" % (endpoint)
    params = { 'query': query }
    headers = { 
      'content-type': 'application/x-www-form-urlencoded', 
      'accept': 'text/plain' 
    }
    (response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
    
    print "Response %s" % response.status
    
    graph = rdflib.ConjunctiveGraph()
    graph.parse(rdflib.parser.StringInputSource(content), format="nt")

    print "Loaded %d triples" % len(graph)

    class Course(rdfalchemy.rdfSubject):
        rdf_type = LUCI.Course
        title = rdfalchemy.rdfSingle(DC.title)
        subjects = rdfalchemy.rdfSingle(DC.subject)
        description = rdfalchemy.rdfSingle(DC.description)
        qualification = rdfalchemy.rdfSingle(LUCI.qualification)
        application = rdfalchemy.rdfSingle(LUCI.applicationProcedure)
        offerings = rdfalchemy.rdfMultiple(LUCI.specifies)
        #TODO: rdfalchemy doesn't load abstract data - checked already abstract is created in sparql query!! what's the problem.. T.T!!
        abstract = rdfalchemy.rdfSingle(LUCI.abstract)
        learningoutcome = rdfalchemy.rdfSingle(LUCI.learningOutcome)
    
    rdfalchemy.rdfSubject.db = graph
    print course_id
    
    #filter_by didn't work
    #Course.filter_by(resUri = course_id)
    
    class CourseModel:
        def __init__(self, cid, title, abstract, subjects, description, qualification, application, offerings, learningoutcome):
            self.cid = cid
            self.title = title
            self.abstract = abstract
            self.subjects = subjects
            self.description = description
            self.qualification = qualification
            self.application = application
            self.offerings = offerings
            self.learningoutcome = learningoutcome
        
        def set_qualification(self, qualification):
            self.qualification = qualification
            
    
    flag = 0
    for course in Course.ClassInstances():
        flag = 1
        print "."
        courseModel = CourseModel(course.resUri, course.title, course.abstract, course.subjects, html.escape(course.description), course.qualification, course.application, course.offerings, course.learningoutcome)
    ''' 
    for offering in course.offerings:
        offering = offering[offering.find("#")+1:]
        
    for offering in course.offerings:    
        print offering
    '''
    
    'empty the menu navigation list'
    breadcrumb[:] =[];
    bcmodel = breadcrumbModel("/ce/course/"+courseModel.cid[courseModel.cid.find("#")+1:]+"/", "Course")
    breadcrumb.append(bcmodel);
       
    if flag == 0:
        return
    return courseModel, breadcrumb

def get_offeringDetail(offering_id):
    offering_id = "<http://luci.uwl.ac.uk/course_linkeddata/Presentation#"+offering_id+">"
    query = """PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX luci:<http://luci.uwl.ac.uk/course_linkeddata/> 
    PREFIX dc:<http://purl.org/dc/elements/1.1/> 
    select ?offering ?attendancemode ?duration ?start ?studymode ?applyuntil ?attendancepattern 
        ?url ?title ?applyfrom ?prerequisite ?location ?assessment ?school
        where { ?offering rdf:type luci:Presentation ; 
                    dc:title ?title .
        optional { ?offering luci:attendanceMode ?attendancemode .} 
        optional { ?offering luci:duration  ?duration .}  
        optional { ?offering luci:start ?start .} 
        optional { ?offering luci:studyMode ?studymode .}  
        optional { ?offering luci:applyUntil ?applyuntil .}  
        optional { ?offering luci:attendancePattern ?attendancepattern .}  
        optional { ?offering luci:url ?url .} 
        optional { ?offering luci:applyFrom ?applyfrom .} 
        optional { ?offering luci:prerequisite ?prerequisite .} 
        optional { ?offering luci:isOfferedAt ?location .} 
        optional { ?offering luci:assessment ?assessment .}  
        optional { ?offering luci:school ?school .} 
      filter (?offering=%s)}"""  %(offering_id)
      
    print "POSTing SPARQL query to %s" % (endpoint)
    params = { 'query': query }
    headers = { 
      'content-type': 'application/x-www-form-urlencoded', 
      'accept': 'application/sparql-results+json'  
    }
    (response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
    print "Response %s" % response.status
    if content is None:
        return
    results = json.loads(content) 
    
    class OfferingModel:
        def __init__(self, oid):
            self.oid = oid
        def setAttendanceMode(self, attendancemode):
            self.attendancemode = attendancemode
        def setDuration(self, duration):
            self.duration = duration
        def setStart(self, start):
            self.start = start
        def setStudyMode(self, studymode):
            self.studymode = studymode
        def setApplyUntil(self, applyuntil):
            self.applyuntil = applyuntil
        def setAttendancePattern(self, attendancepattern):
            self.attendancepattern = attendancepattern
        def setUrl(self, url):
            self.url = url
        def setTitle(self, title):
            self.title = title
        def setApplyFrom(self, applyfrom):
            self.applyfrom = applyfrom
        def setPrerequisite(self, prerequisite):
            self.prerequisite = prerequisite
        def setLocation(self, location):
            self.location = location
        def setAssessment(self, assessment):
            self.assessment = assessment
        def setSchool(self, school):
            self.school = school
    
    flag = 0
    for result in results['results']['bindings']:
        flag = 1
        print "."
        offering = OfferingModel(result['offering']['value'])
        try: offering.setAttendanceMode(result['attendancemode']['value'])
        except KeyError: print "no aatendancemode"
        try: offering.setDuration(result['duration']['value'])
        except KeyError: print "no duration"
        try: offering.setStudyMode(result['studymode']['value'])
        except KeyError: print "no study mode"
        try: offering.setStart(result['start']['value'])
        except KeyError: print "no start"
        try: offering.setApplyUntil(result['applyuntil']['value'])
        except KeyError: print "no apply until"
        try: offering.setAttendancePattern(result['attendancepattern']['value'])
        except KeyError: print "no attendance pattern" 
        try: offering.setUrl(result['url']['value'])
        except KeyError: print "no url"
        try: offering.setTitle(result['title']['value'])
        except KeyError: print "no title"
        try: offering.setApplyFrom(result['applyfrom']['value'])
        except KeyError: print "no apply from"
        try: offering.setPrerequisite(result['prerequisite']['value'])
        except KeyError: print "no prerequisite"
        try: offering.setLocation(result['location']['value'])
        except KeyError: print "no location"
        try: offering.setAssessment(result['assessment']['value'])
        except KeyError: print "no assessment"
        try: offering.setSchool(result['school']['value'])
        except KeyError: print "no school"

    print breadcrumb.__len__()

    if(breadcrumb.__len__() == 1):
        bcmodel = breadcrumbModel("/ce/presentation/"+offering.oid[offering.oid.find("#")+1:]+"/", " > Presentation")
        breadcrumb.append(bcmodel);
        print "add"
    elif(breadcrumb.__len__() > 2):
        breadcrumb.pop()
        print "delete"

    if flag == 0:
        return
    return offering, breadcrumb

def get_qualificationDetail(qualification_id):
    qualification_id = "<http://luci.uwl.ac.uk/course_linkeddata/Qualification#"+qualification_id+">"
    query = """PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX luci:<http://luci.uwl.ac.uk/course_linkeddata/> 
    PREFIX dc:<http://purl.org/dc/elements/1.1/> 
    select ?qualification ?title ?abbr ?educationlevel ?awardedby ?accreditedby 
    where { ?qualification rdf:type luci:Qualification ; 
                    luci:abbr ?abbr .
     optional { ?qualification luci:title ?title .}
     optional { ?qualification luci:educationLevel ?educationlevel .}
     optional { ?qualification luci:awardedBy ?awardedby .}
     optional { ?qualification luci:accreditedBy ?accreditedby .}
     filter (?qualification = %s)}"""  %(qualification_id)
      
    print "POSTing SPARQL query to %s" % (endpoint)
    params = { 'query': query }
    headers = { 
      'content-type': 'application/x-www-form-urlencoded', 
      'accept': 'application/sparql-results+json'  
    }
    (response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
    print "Response %s" % response.status
    if content is None:
        return
    results = json.loads(content) 
    
    class QualificationModel:
        def __init__(self, qid):
            self.qid = qid
        def setTitle(self, title):
            self.title = title
        def setAbbr(self, abbr):
            self.abbr = abbr
        def setEducationLevel(self, educationlevel):
            self.educationlevel = educationlevel
        def setAwardedBy(self, awardedby):
            self.awardedby = awardedby
        def setAccreditedBy(self, accreditedby):
            self.accreditedby = accreditedby
            
    flag = 0
    for result in results['results']['bindings']:
        flag = 1
        print "."
        qualification = QualificationModel(result['qualification']['value'])
        try: qualification.setTitle(result['title']['value'])
        except KeyError: print "no title"
        try: qualification.setAbbr(result['abbr']['value'])
        except KeyError: print "no abbr"
        try: qualification.setEducationLevel(result['educationlevel']['value'])
        except KeyError: print "no education level"
        try: qualification.setAccreditedBy(result['accreditedby']['value'])
        except KeyError: print "no accreditedby"
        try: qualification.setAccreditedBy(result['awardedby']['value'])
        except KeyError: print "no awardedby"

    if(breadcrumb.__len__() == 1):
       bcmodel = breadcrumbModel("/ce/qualification/"+qualification.qid[qualification.qid.find("#")+1:]+"/", " > Qualification")
       breadcrumb.append(bcmodel);
    
    if flag == 0:
        return
    return qualification, breadcrumb

def get_locationDetail(location_id):
    
    #TODO: put back the location_id as taking the parameter 
    location_id = "<http://luci.uwl.ac.uk/course_linkeddata/Location#"+location_id+">"
    #location_id = "<http://luci.uwl.ac.uk/course_linkeddata/Location#uwl_Ealing>"
    query = """PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX luci:<http://luci.uwl.ac.uk/course_linkeddata/> 
    PREFIX dc:<http://purl.org/dc/elements/1.1/> 
    PREFIX owl:<http://www.w3.org/2002/07/owl#>    
    select ?location ?title ?ord_location ?email ?fax ?phone ?address ?postcode 
    where { ?location rdf:type luci:Location ; 
                    dc:title ?title . 
    optional { ?location owl:sameAs  ?ord_location .} 
    optional { ?location luci:email ?email .}
    optional { ?location luci:fax ?fax .}
    optional { ?location luci:phone ?phone .}
    optional { ?location luci:address ?address .}
    optional { ?location luci:postcode ?postcode .} 
     filter (?location = %s)}"""  %(location_id)
      
    print "POSTing SPARQL query to %s" % (endpoint)
    params = { 'query': query }
    headers = { 
      'content-type': 'application/x-www-form-urlencoded', 
      'accept': 'application/sparql-results+json'  
    }
    (response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
    print "Response %s" % response.status
    if content is None:
        return
    results = json.loads(content) 
    
    class LocationModel:
        def __init__(self, lid):
            self.lid = lid
        def setTitle(self, title):
            self.title = title
        def setAddress(self, address):
            self.address = address
        def setPostcode(self, postcode):
            self.postcode = postcode
        def setOrdLocation(self, ord_location):
            self.ord_location = ord_location
        def setPhone(self, phone):
            self.phone = phone
        def setFax(self, fax):
            self.fax = fax
        def setEmail(self, email):
            self.email = email
        
        
    flag = 0
    for result in results['results']['bindings']:
        flag = 1
        print "."
        location = LocationModel(result['location']['value'])
        try: location.setTitle(result['title']['value'])
        except KeyError: print "no title"
        try: location.setAddress(result['address']['value'])
        except KeyError: print "no address"
        try: location.setPostcode(result['postcode']['value'])
        except KeyError: print "no postcode"
        try: location.setOrdLocation(result['ord_location']['value'])
        except KeyError: print "no ord_location"
        try: location.setPhone(result['phone']['value'])
        except KeyError: print "no phone"
        try: location.setFax(result['fax']['value'])
        except KeyError: print "no fax"
        try: location.setEmail(result['email']['value'])
        except KeyError: print "no email"


    if flag == 0:
        return
    
    try: address = location.postcode
    except AttributeError: address = location.title + ", UK"
    gmaps = GoogleMaps("AIzaSyAIL6XCmJIxxxRyOpDR5vb5oWVONVzhQeQ")
    lat, lng = gmaps.address_to_latlng(address)
    
    if(breadcrumb.__len__() == 2):
        bcmodel = breadcrumbModel("/ce/location/"+location.lid[location.lid.find("#")+1:]+"/", " > Location")
        breadcrumb.append(bcmodel);
       
    return location, lat, lng, breadcrumb


def get_campus():
    query = """PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX luci:<http://luci.uwl.ac.uk/course_linkeddata/> 
    PREFIX dc:<http://purl.org/dc/elements/1.1/> 
    PREFIX owl:<http://www.w3.org/2002/07/owl#>    
    select distinct ?title
    where {?location rdf:type luci:Location ;
            dc:title ?title . }"""
    
    print "POSTing SPARQL query to %s" % (endpoint)
    params = { 'query': query }
    headers = { 
      'content-type': 'application/x-www-form-urlencoded', 
      'accept': 'application/sparql-results+json'  
    }
    (response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
    print "Response %s" % response.status
    if content is None:
        return
    results = json.loads(content) 
    
    campus_list = []
    flag = 0
    for result in results['results']['bindings']:
        flag = 1
        print "."
        campus_list.append(result['title']['value'])
        
    if flag == 0:
        return
    return campus_list

    
def get_school():
    
    query = """PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX luci:<http://luci.uwl.ac.uk/course_linkeddata/> 
    PREFIX dc:<http://purl.org/dc/elements/1.1/> 
    PREFIX owl:<http://www.w3.org/2002/07/owl#>    
    select distinct ?school
    where {?offering rdf:type luci:Presentation ;
            luci:school ?school . }"""
    
    print "POSTing SPARQL query to %s" % (endpoint)
    params = { 'query': query }
    headers = { 
      'content-type': 'application/x-www-form-urlencoded', 
      'accept': 'application/sparql-results+json'  
    }
    (response, content) = httplib2.Http().request(endpoint, 'POST', urllib.urlencode(params), headers=headers)
    print "Response %s" % response.status
    if content is None:
        return
    results = json.loads(content) 
    
    school_list = []
    flag = 0
    for result in results['results']['bindings']:
        flag = 1
        print "."
        school_list.append(result['school']['value'])
        
    if flag == 0:
        return
    return school_list
