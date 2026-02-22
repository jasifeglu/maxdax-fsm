import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

class AdminDashboardPage extends StatelessWidget {
  const AdminDashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Live Technician Map')),
      body: StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
        stream: FirebaseFirestore.instance.collection('live_locations').snapshots(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }

          final docs = snapshot.data!.docs;
          if (docs.isEmpty) {
            return const Center(child: Text('No technician locations yet.'));
          }

          final markers = docs.map((doc) {
            final data = doc.data();
            return Marker(
              markerId: MarkerId(doc.id),
              position: LatLng(
                (data['lat'] as num).toDouble(),
                (data['lng'] as num).toDouble(),
              ),
              infoWindow: InfoWindow(
                title: data['technicianId']?.toString() ?? 'Unknown technician',
                snippet: data['event']?.toString(),
              ),
            );
          }).toSet();

          final firstData = docs.first.data();
          final initialCameraPosition = CameraPosition(
            target: LatLng(
              (firstData['lat'] as num).toDouble(),
              (firstData['lng'] as num).toDouble(),
            ),
            zoom: 11,
          );

          return GoogleMap(
            initialCameraPosition: initialCameraPosition,
            markers: markers,
            myLocationEnabled: false,
            myLocationButtonEnabled: false,
          );
        },
      ),
    );
  }
}
