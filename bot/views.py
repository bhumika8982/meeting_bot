import threading
import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .meeting_bot import join_zoom_meeting

@csrf_exempt
def start_bot(request):
    if request.method == 'POST':
        meeting_id = request.POST.get('meeting_id')
        passcode = request.POST.get('passcode')

        if not meeting_id:
            return JsonResponse({"error": "Meeting ID missing hai!"}, status=400)

        # Meeting ID clean karein
        meeting_id = str(meeting_id).replace(" ", "").replace("-", "")

        thread = threading.Thread(target=join_zoom_meeting, args=(meeting_id, passcode))
        thread.daemon = True
        thread.start()

        return JsonResponse({"status": "Success", "message": f"Bot meeting {meeting_id} join kar raha hai!"})
    
    return JsonResponse({"error": "Only POST allowed"}, status=405)

def get_meeting_data(request, meeting_id):
    clean_id = str(meeting_id).replace(" ", "").replace("-", "")
    mom_path = f"outputs/MOM_{clean_id}.txt"
    if os.path.exists(mom_path):
        with open(mom_path, "r", encoding="utf-8") as f:
            return JsonResponse({"meeting_id": clean_id, "mom": f.read()})
    return JsonResponse({"error": "Summary taiyar nahi hai"}, status=404)

# YE FUNCTION MISSING THA JISSE ERROR AA RAHI HAI
@csrf_exempt
def delete_meeting_data(request, meeting_id):
    clean_id = str(meeting_id).replace(" ", "").replace("-", "")
    try:
        # File paths
        audio = f"recordings/meeting_{clean_id}.wav"
        mom = f"outputs/MOM_{clean_id}.txt"
        if os.path.exists(audio): os.remove(audio)
        if os.path.exists(mom): os.remove(mom)
        return JsonResponse({"status": "Deleted", "message": f"Data for {clean_id} deleted."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)