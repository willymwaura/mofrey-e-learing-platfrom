from .models import Course, Subtopic, Episodes,Marks

def get_module_ids_ordered_by_subtopics_and_date(course_id):
    # Get the subtopics associated with the course
    subtopics = Subtopic.objects.filter(course=course_id).order_by('date')

    # Initialize a list to store module IDs
    module_ids = []

    # Iterate through subtopics
    for subtopic in subtopics:
        # Get modules associated with the current subtopic
        modules = Episodes.objects.filter(subtopic=subtopic.id).order_by('date')
        # Add module IDs to the list
        module_ids.extend(modules.values_list('id', flat=True))

    return module_ids

def give_unclocked_ids_list(course_modules_list,user_id):
    try:
        latest_mark = Marks.objects.filter(status=True,userId=user_id).latest('date')
        latest_module_id = latest_mark.moduleId

        position = course_modules_list.index(latest_module_id)
        modules_to_view=position+2

        unlocked_module_ids = course_modules_list[:modules_to_view]
        print(unlocked_module_ids)
        return unlocked_module_ids
    except:
        modules_to_view=1
        print(modules_to_view)
        unlocked_module_ids = course_modules_list[:modules_to_view]
        print(unlocked_module_ids)
        return unlocked_module_ids
    
