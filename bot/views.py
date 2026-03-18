import threading
import os
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


from .meeting_bot import join_zoom_meeting
from .recorder import stop_recording  

def get_bot_paths(meeting_id):
    clean_id = str(meeting_id).replace(" ", "").replace("-", "")
    recordings_dir = os.path.join(settings.BASE_DIR, 'recordings')
    return {
        "id": clean_id,
        "audio": os.path.join(recordings_dir, f"meeting_{clean_id}.wav"),
        "transcript": os.path.join(recordings_dir, f"transcript_{clean_id}.txt"),
        "mom": os.path.join(recordings_dir, f"mom_{clean_id}.md")
    }


@csrf_exempt
def start_bot(request):
    if request.method == 'POST':
        meeting_id = request.POST.get('meeting_id')
        passcode = request.POST.get('passcode')

        if not meeting_id:
            return JsonResponse({"error": "Meeting ID missing hai!"}, status=400)

        paths = get_bot_paths(meeting_id)

       
        thread = threading.Thread(target=join_zoom_meeting, args=(paths['id'], passcode))
        thread.daemon = True
        thread.start()

        return JsonResponse({
            "status": "Success", 
            "meeting_id": paths['id'],
            "message": f"Bot meeting {paths['id']} join kar raha hai."
        })
    return JsonResponse({"error": "Only POST allowed"}, status=405)


@csrf_exempt
def stop_bot_service(request, meeting_id):
    if request.method == 'POST':
        paths = get_bot_paths(meeting_id)
       
        stop_recording(paths['audio']) 
        return JsonResponse({"status": "Stopped", "message": "Bot ko stop signal bhej diya gaya hai."})
    return JsonResponse({"error": "Only POST allowed"}, status=405)


def get_meeting_results(request, meeting_id):
    paths = get_bot_paths(meeting_id)
    
    if os.path.exists(paths['mom']):
        try:
            with open(paths['transcript'], "r", encoding="utf-8") as t, \
                 open(paths['mom'], "r", encoding="utf-8") as m:
                return JsonResponse({
                    "status": "Completed",
                    "meeting_id": paths['id'],
                    "transcript": t.read(),
                    "mom_summary": m.read()
                })
        except Exception as e:
            return JsonResponse({"error": f"File reading error: {str(e)}"}, status=500)
    
    return JsonResponse({
        "status": "Processing", 
        "message": "Results abhi taiyar nahi hain. Transcript ya MOM generate ho raha hai."
    }, status=404)


@csrf_exempt
def delete_meeting_data(request, meeting_id):
    if request.method not in ['POST', 'DELETE']:
         return JsonResponse({"error": "Use DELETE or POST method"}, status=405)

    paths = get_bot_paths(meeting_id)
    files_to_delete = [paths['audio'], paths['transcript'], paths['mom']]
    deleted_files = []

    try:
        for file_path in files_to_delete:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_files.append(os.path.basename(file_path))
        
        return JsonResponse({
            "status": "Deleted", 
            "meeting_id": paths['id'],
            "removed_files": deleted_files
        })
    except Exception as e:
        return JsonResponse({"error": f"Deletion failed: {str(e)}"}, status=500)