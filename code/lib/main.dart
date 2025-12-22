import 'package:flutter/material.dart';
import 'animated_background.dart';
import 'dart:ui';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Login Form',
      debugShowCheckedModeBanner: false,
      showSemanticsDebugger: false,
      home: Scaffold(
        body: Stack(
          children: [
            // $REQ_LOGIN_FORM_012: The animated scrolling background
            const Positioned.fill(
              child: AnimatedBackground(),
            ),
            // $REQ_LOGIN_FORM_001: Form centered in viewport
            // $REQ_LOGIN_FORM_011: Remains centered at all viewport sizes (320px+)
            Center(
              child: LoginForm(),
            ),
          ],
        ),
      ),
    );
  }
}

class LoginForm extends StatefulWidget {
  const LoginForm({super.key});

  @override
  State<LoginForm> createState() => _LoginFormState();
}

class _LoginFormState extends State<LoginForm> {
  bool _stayLoggedIn = false; // $REQ_LOGIN_FORM_008: Unchecked by default

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 400, // $REQ_LOGIN_FORM_002: Fixed width of approximately 400 pixels
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        // $REQ_LOGIN_FORM_003: Semi-transparent purple/hot pink background with glassmorphism
        color: const Color(0xFFBA68C8).withOpacity(0.3),
        // $REQ_LOGIN_FORM_004: Subtle white border and rounded corners
        border: Border.all(
          color: Colors.white.withOpacity(0.3),
          width: 1,
        ),
        borderRadius: BorderRadius.circular(16),
        // $REQ_LOGIN_FORM_005: Soft drop shadow
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: BackdropFilter(
          // $REQ_LOGIN_FORM_003: Frosted glass blur effect
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // $REQ_LOGIN_FORM_006: "Login" heading at the top
              const Text(
                'Login',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),

              // $REQ_LOGIN_FORM_007: Email field with label and hint text
              const Text(
                'Email',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                decoration: InputDecoration(
                  hintText: 'you@example.com', // $REQ_LOGIN_FORM_007
                  hintStyle: TextStyle(
                    color: Colors.white.withOpacity(0.5),
                  ),
                  filled: true,
                  fillColor: Colors.white.withOpacity(0.1),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide(
                      color: Colors.white.withOpacity(0.3),
                    ),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide(
                      color: Colors.white.withOpacity(0.3),
                    ),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: const BorderSide(
                      color: Colors.white,
                    ),
                  ),
                ),
                style: const TextStyle(color: Colors.white),
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 16),

              // $REQ_LOGIN_FORM_008: "Stay logged in" checkbox
              Row(
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: Checkbox(
                      value: _stayLoggedIn,
                      onChanged: (value) {
                        setState(() {
                          _stayLoggedIn = value ?? false;
                        });
                      },
                      fillColor: MaterialStateProperty.resolveWith((states) {
                        if (states.contains(MaterialState.selected)) {
                          return Colors.white;
                        }
                        return Colors.white.withOpacity(0.3);
                      }),
                      checkColor: const Color(0xFFBA68C8),
                    ),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'Stay logged in',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // $REQ_LOGIN_FORM_009: "Continue" button (full width, accent color)
              // $REQ_LOGIN_FORM_010: Display only - does not submit
              ElevatedButton(
                onPressed: () {
                  // Display only - no action
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFEC407A), // Hot pink/accent color
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  elevation: 0,
                ),
                child: const Text(
                  'Continue',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
