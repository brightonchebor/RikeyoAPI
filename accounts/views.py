from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView
from .serializers import *

from rest_framework.response import Response
from rest_framework import status
from .utils import send_code_to_user
from .models import OneTimePassword
from rest_framework.permissions import IsAuthenticated
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import User
from rest_framework.exceptions import NotFound

from django.utils import timezone

from geopy.distance import great_circle


# Create your views here.
class UserRegisterView(GenericAPIView):
    serializer_class = UserRegisterSerializer

   
    def post(self, request):
        user_data = request.data
        role = user_data.get('role')

        if role=='manager':
            if User.objects.filter(role='manager').exists():
                return Response({
                    'message':'Only one manager is allowed'
                } ,status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=user_data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            send_code_to_user(user['email'])
            #send email function user['email']
            return Response({
                'data':user,
                'message':f'hi {user['first_name']} thanks for signing up as RiseKenya {user['role']}, a passcode has been sent to your email',
              }, status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyUserEmail(GenericAPIView):

    def post(self, request):
        otpcode = request.data.get('otp')
        try:
            user_code_obj = OneTimePassword.objects.get(code=otpcode)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    'message':'email account verified successfully'
                }, status=status.HTTP_200_OK)
            return Response({
                'message':'code is invalid user already exist'
            }, status=status.HTTP_204_NO_CONTENT)
        
        except OneTimePassword.DoesNotExist:
            return Response({
                'message':'passcode not provided'
            }, status=status.HTTP_404_NOT_FOUND)
        
class LoginUserView( GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={
                'request':request
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    
class TestAunthenticationView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data={
            'msg':'it works'
        }
        return Response(data, status=status.HTTP_200_OK)

class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request':request})    
        serializer.is_valid(raise_exception=True)
        return Response({
            'message':'a link has been sent to your email to reset your password'
        }, status=status.HTTP_200_OK)

class PasswordResetConfirm(GenericAPIView):
    
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({
                    'message':'token is invalid or has expired'
                }, status=status.HTTP_401_UNAUTHORIZED)
            return Response({
                'success':True,
                'message':'credentials are valid',
                'uidb64':uidb64,
                'token':token,
            }, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError:
            return Response({
                'message':'token is invalid or has expired'
            }, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request): # we are updatinng the pwd
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            'message':'password reset successful'
        }, status=status.HTTP_200_OK)
    
class LogoutUserView(GenericAPIView):
    serializer_class = LogoutUsererializer    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



class AttendanceView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        action = request.data.get('action')  # 'clock_in' or 'clock_out'
        date = request.data.get('date')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        

        attendance_data = {
            'user': request.user.id,
            'action': action,
            'date': date,
            
        }
        
        # Geofence parameters
        office_lat = 14.67
        office_long = 29.65
        geofence_center = (office_lat, office_long)  
        geofence_radius = 100  # in meters

        if not action:
            return Response({"error": "Action must be provided ('clock_in' or 'clock_out')."}, status=status.HTTP_400_BAD_REQUEST)


        # Validate required fields
        if not date or latitude is None or longitude is None:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert latitude and longitude to floats
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return Response({"error": "Latitude and longitude must be valid numbers."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if within geofence
        distance = great_circle(geofence_center, (latitude, longitude)).meters
        if distance > geofence_radius:
            return Response({"error": "Location outside geofence."}, status=status.HTTP_403_FORBIDDEN)
    
        # Retrieve or create the attendance record
        attendance, created = Attendance.objects.get_or_create(
                        user=request.user,  
                        date=date,
                        
                       

                        )
        
        if action == 'clock_in':
            if attendance.clock_in_time:
                return Response({"error": "You have already clocked in for the day."}, status=status.HTTP_400_BAD_REQUEST)
            
      
            attendance.clock_in_time = timezone.now()
            attendance.clock_in_location_latitude = latitude
            attendance.clock_in_location_longitude = longitude
            


        elif action == 'clock_out':
            if not attendance.clock_in_time:
                return Response({"error": "You must clock in before clocking out."}, status=status.HTTP_400_BAD_REQUEST)
            if attendance.clock_out_time:
                return Response({"error": "You have already clocked out for the day."}, status=status.HTTP_400_BAD_REQUEST)
            
            # attendance_data['clock_out_time'] = timezone.now()
            # attendance_data['clock_out_location_latitude'] = latitude
            # attendance_data['clock_out_location_longitude'] = longitude

            attendance.clock_out_time = timezone.now()
            attendance.clock_out_location_latitude = latitude
            attendance.clock_out_location_longitude = longitude

        attendance.save()
             
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_200_OK if created else status.HTTP_202_ACCEPTED)

class UserListByRoleView(ListAPIView):
    serializer_class = AllUSersSerializer
    permission_classes = [IsAuthenticated]
   

    def get_queryset(self):
        role = self.kwargs.get('role')
        if role not in [choice[0] for choice in User.CHOICES]:
            raise NotFound(detail="Role not found.")
        return User.objects.filter(role=role)
    
class SingleUserView(RetrieveAPIView):
    serializer_class = AllUSersSerializer
    permission_classes = [IsAuthenticated]
    

    def get_queryset(self):
        # Retrieve only users with a specific role
        return User.objects.filter(role=self.kwargs['role'])

    def get_object(self):
        queryset = self.get_queryset()
        user_id = self.kwargs['id']
        try:
            return queryset.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound(detail="User not found.")    
       
class TeacherAttendanceHistoryView(ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    

    def get_queryset(self):
        # Check if the user is a manager or admin
        if self.request.user.role in ['manager', 'admin']:
            # Managers and admins can view all attendance records
            return Attendance.objects.all().order_by('-date')
        else:
            # Teachers can view only their own attendance records
            return Attendance.objects.filter(user=self.request.user).order_by('-date')       
        
class UserDeleteView(DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)        

        