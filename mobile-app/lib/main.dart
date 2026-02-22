import 'package:flutter/material.dart';
import 'features/auth/presentation/login_page.dart';

void main() {
  runApp(const MaxdaxApp());
}

class MaxdaxApp extends StatelessWidget {
  const MaxdaxApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MAXDAX FSM',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const LoginPage(),
    );
  }
}
