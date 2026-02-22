import 'dart:async';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_background_service/flutter_background_service.dart';

import '../models/technician_action.dart';
import 'location_tracking_service.dart';

class LocationEventLogger {
  LocationEventLogger({
    required this.trackingService,
    FirebaseFirestore? firestore,
  }) : _firestore = firestore ?? FirebaseFirestore.instance;

  final LocationTrackingService trackingService;
  final FirebaseFirestore _firestore;

  StreamSubscription<Object?>? _bgLocationSubscription;

  Future<void> start() async {
    await trackingService.initialize();

    _bgLocationSubscription = FlutterBackgroundService()
        .on('location_update')
        .listen((dynamic event) async {
      if (event is! Map) {
        return;
      }

      await _firestore
          .collection('live_locations')
          .doc(trackingService.technicianId)
          .set({
        'technicianId': trackingService.technicianId,
        'event': 'background_ping',
        'lat': event['lat'],
        'lng': event['lng'],
        'speed': event['speed'],
        'heading': event['heading'],
        'timestamp': FieldValue.serverTimestamp(),
      });
    });
  }

  Future<void> saveActionLocation({
    required String jobId,
    required TechnicianAction action,
  }) {
    return trackingService.publishActionLocation(
      jobId: jobId,
      action: action.label,
    );
  }

  Future<void> dispose() async {
    await _bgLocationSubscription?.cancel();
  }
}
