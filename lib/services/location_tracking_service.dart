import 'dart:async';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:geolocator/geolocator.dart';

class LocationTrackingService {
  LocationTrackingService({
    required this.technicianId,
    FirebaseFirestore? firestore,
  }) : _firestore = firestore ?? FirebaseFirestore.instance;

  final String technicianId;
  final FirebaseFirestore _firestore;

  static const _service = FlutterBackgroundService();

  Future<void> initialize() async {
    final enabled = await Geolocator.isLocationServiceEnabled();
    if (!enabled) {
      throw Exception('Location services are disabled.');
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }

    if (permission == LocationPermission.deniedForever ||
        permission == LocationPermission.denied) {
      throw Exception('Location permissions are denied.');
    }

    await _service.configure(
      iosConfiguration: IosConfiguration(
        autoStart: true,
        onForeground: _onStart,
        onBackground: _onIosBackground,
      ),
      androidConfiguration: AndroidConfiguration(
        onStart: _onStart,
        autoStart: true,
        isForegroundMode: true,
        foregroundServiceNotificationId: 101,
      ),
    );

    await _service.startService();
  }

  Future<void> publishActionLocation({
    required String jobId,
    required String action,
  }) async {
    final position = await Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
      ),
    );

    final payload = {
      'technicianId': technicianId,
      'jobId': jobId,
      'event': action,
      'lat': position.latitude,
      'lng': position.longitude,
      'speed': position.speed,
      'heading': position.heading,
      'timestamp': FieldValue.serverTimestamp(),
    };

    await _firestore.collection('location_events').add(payload);
    await _firestore.collection('live_locations').doc(technicianId).set(payload);
  }

  @pragma('vm:entry-point')
  static void _onStart(ServiceInstance service) {
    Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.bestForNavigation,
        distanceFilter: 20,
      ),
    ).listen((position) {
      service.invoke('location_update', {
        'lat': position.latitude,
        'lng': position.longitude,
        'speed': position.speed,
        'heading': position.heading,
      });
    });
  }

  @pragma('vm:entry-point')
  static Future<bool> _onIosBackground(ServiceInstance service) async {
    return true;
  }
}
