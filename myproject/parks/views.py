from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import LightZone, SystemLog
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .esp_control import send_command_to_esp
from .models import UserData  # модель, где хранится ssid
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('personal_space')
        else:
            return render(request, 'parks/login.html', {'error': 'Неверный логин или пароль'})

    return render(request, 'parks/login.html')


@login_required
def personal_space_view(request):
    userdata = request.user.userdata

    if request.method == 'POST':
        ssid = request.POST.get('ssid')
        if ssid:
            userdata.ssid = ssid
            userdata.save()
            messages.success(request, "SSID обновлён.")

    return render(request, 'parks/personal_space.html', {'userdata': userdata})


def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_exempt
def esp_update_status(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            ssid = body.get('ssid')
            data = body.get('status')

            user_data = UserData.objects.get(ssid=ssid)
            user_data.data = data
            user_data.save()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Only POST allowed'}, status=405)

@csrf_exempt
@login_required
def toggle_zone(request, zone_number):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    try:
        zone_number = int(zone_number)
        zone, _ = LightZone.objects.get_or_create(user=request.user, zone_number=zone_number)

        new_state = not zone.is_on

        ssid = UserData.objects.get(user=request.user).ssid
        success = send_command_to_esp(ssid, zone_number, new_state)

        if success:
            zone.is_on = new_state
            zone.save()
            SystemLog.objects.create(
                user=request.user,
                zone_number=zone_number,
                action='on' if new_state else 'off'
            )
            return JsonResponse({'status': 'ok', 'new_state': zone.is_on})
        else:
            return JsonResponse({'status': 'error', 'message': 'ESP не ответил'}, status=500)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def cabinet(request):
    userdata = UserData.objects.get(user=request.user)
    zones = {z.zone_number: z.is_on for z in LightZone.objects.filter(user=request.user)}

    return render(request, 'parks/personal_space.html', {
        'userdata': userdata,
        'zones': zones,
    })

@login_required
def system_logs(request):
    logs = SystemLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'parks/logs.html', {'logs': logs})

ESP_COMMAND_TIMEOUT = 5  # секунд

@login_required
def enable_service_mode(request):
    if request.method == 'POST':
        zones = LightZone.objects.filter(user=request.user)
        failed_zones = []

        for zone in zones:
            try:
                esp_url = f"http://{request.user.userdata.ssid}/zone/{zone.zone_number}/on"
                response = requests.get(esp_url, timeout=ESP_COMMAND_TIMEOUT)

                if response.status_code == 200 and 'OK' in response.text:
                    zone.is_on = True
                    zone.save()
                    SystemLog.objects.create(
                        user=request.user,
                        zone_number=zone.zone_number,
                        action='on'
                    )
                else:
                    failed_zones.append(zone.zone_number)

            except Exception:
                failed_zones.append(zone.zone_number)

        if failed_zones:
            messages.error(request, f"Ошибка включения зон: {', '.join(map(str, failed_zones))}")
        else:
            messages.success(request, "Сервисный режим активирован: все зоны включены.")

        return redirect('personal_space')
