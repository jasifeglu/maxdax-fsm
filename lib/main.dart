import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';

import 'admin/admin_dashboard_page.dart';
import 'models/technician_action.dart';
import 'services/location_event_logger.dart';
import 'services/location_tracking_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  runApp(const MaxdaxApp());
}

class MaxdaxApp extends StatelessWidget {
  const MaxdaxApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Maxdax FSM',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const TechnicianHomePage(),
      routes: {
        '/admin': (_) => const AdminDashboardPage(),
      },
    );
  }
}

class TechnicianHomePage extends StatefulWidget {
  const TechnicianHomePage({super.key});

  @override
  State<TechnicianHomePage> createState() => _TechnicianHomePageState();
}

class _TechnicianHomePageState extends State<TechnicianHomePage> {
  final _jobIdController = TextEditingController();
  late final LocationEventLogger _logger;
  String _message = 'Tracking starting...';

  @override
  void initState() {
    super.initState();
    _logger = LocationEventLogger(
      trackingService: LocationTrackingService(technicianId: 'tech_001'),
    );
    _initializeTracking();
  }

  Future<void> _initializeTracking() async {
    try {
      await _logger.start();
      if (!mounted) return;
      setState(() => _message = 'Background tracking enabled');
    } catch (e) {
      if (!mounted) return;
      setState(() => _message = 'Tracking failed: $e');
    }
  }

  Future<void> _save(TechnicianAction action) async {
    final jobId = _jobIdController.text.trim();
    if (jobId.isEmpty) {
      setState(() => _message = 'Enter a job id first.');
      return;
    }

    await _logger.saveActionLocation(jobId: jobId, action: action);
    if (!mounted) return;
    setState(() => _message = 'Saved ${action.label} location for $jobId');
  }

  @override
  void dispose() {
    _jobIdController.dispose();
    _logger.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Technician Tasks')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'GPS tracking runs automatically in the background. '
              'No technician GPS screen is exposed.',
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _jobIdController,
              decoration: const InputDecoration(labelText: 'Job ID'),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                ElevatedButton(
                  onPressed: () => _save(TechnicianAction.checkIn),
                  child: const Text('Check-in'),
                ),
                ElevatedButton(
                  onPressed: () => _save(TechnicianAction.checkOut),
                  child: const Text('Check-out'),
                ),
                ElevatedButton(
                  onPressed: () => _save(TechnicianAction.statusUpdate),
                  child: const Text('Status update'),
                ),
                ElevatedButton(
                  onPressed: () => _save(TechnicianAction.billingSubmit),
                  child: const Text('Billing submit'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(_message),
            const SizedBox(height: 24),
            const Divider(),
            const Text('Admin access:'),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pushNamed('/admin'),
              child: const Text('Open live map dashboard'),
            ),
          ],
        ),
      ),
    );
  }
}
