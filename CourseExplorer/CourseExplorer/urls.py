from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^ce/$', 'CourseExplorer.views.frames'),
    url(r'^ce/top_nav.html$', 'CourseExplorer.views.top_menu'),
    url(r'^ce/blank/$', 'CourseExplorer.views.blank'),
    url(r'^ce/courses/$', 'CourseExplorer.views.course_index'),
    url(r'^ce/schools/$', 'CourseExplorer.views.school_index'),
    url(r'^ce/campuses/$', 'CourseExplorer.views.campus_index'),
    url(r'^ce/course/(?P<course_id>\d+)/$', 'CourseExplorer.views.course_detail'),
    url(r'^ce/presentation/(?P<offering_id>\d+)/$', 'CourseExplorer.views.offering_detail'),
    url(r'^ce/qualification/(?P<qualification_id>\d+)/$', 'CourseExplorer.views.qualification_detail'),
    url(r'^ce/location/(?P<location_id>\d+)/$', 'CourseExplorer.views.location_detail'),
    url(r'^ce/school/(?P<school_title>\d+)/$', 'CourseExplorer.views.school_detail'),
    url(r'^ce/campus/(?P<campus_title>.+)/$', 'CourseExplorer.views.campus_detail'),

    # Examples:
    # url(r'^$', 'CourseExplorer.views.home', name='home'),
    # url(r'^CourseExplorer/', include('CourseExplorer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
