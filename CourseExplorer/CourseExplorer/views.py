'''
Created on Jul 10, 2012

@author: hyeokim
'''
from django.http import HttpResponse
from django.shortcuts import render_to_response
from CourseExplorer import query

def frames(reques):
    return render_to_response('frames.html')

def blank(request):
    return render_to_response('blank.html')

def top_menu(request):
    return render_to_response('top_nav.html')
 
def course_index(request):
    course_list = query.get_course("all", "course")
    return render_to_response('index.html', {'course_list': course_list})

            
def school_index(request):  
    school_list = query.get_school()
    return render_to_response('school_index.html', {'school_list': school_list})

def campus_index(request):
    campus_list = query.get_campus()
    return render_to_response('campus_index.html', {'campus_list': campus_list})


def course_detail(request, course_id):
    course, breadcrumb = query.get_courseDetail(course_id)
    return render_to_response('course_detail.html', {'course': course, 'breadcrumb_list':breadcrumb})

def offering_detail(request, offering_id):
    offering, breadcrumb = query.get_offeringDetail(offering_id)
    return render_to_response('offering_detail.html', {'offering': offering, 'breadcrumb_list':breadcrumb})

def qualification_detail(request, qualification_id):
    qualification, breadcrumb = query.get_qualificationDetail(qualification_id)
    return render_to_response('qualification_detail.html', {'qualification': qualification, 'breadcrumb_list':breadcrumb})

def location_detail(request, location_id):
    location, lat, lang, breadcrumb = query.get_locationDetail(location_id)
    return render_to_response('location_detail.html', {'location': location, 'lat':lat, 'lang':lang, 'breadcrumb_list':breadcrumb})


def school_detail(request, school_title):
    course_list = query.get_course(school_title, "school")
    return render_to_response('index.html', {'course_list': course_list})

def campus_detail(request, campus_title):
    course_list = query.get_course(campus_title, "campus")
    return render_to_response('index.html', {'course_list': course_list})