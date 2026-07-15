import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:go_router/go_router.dart';
import '../../core/auth_service.dart';
import '../../core/api_config.dart';
import '../../shared/widgets/inline_error_text.dart';
import '../../shared/widgets/primary_loading_button.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String _error = '';

  Future<void> _register() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "email": _emailController.text.trim(),
          "password": _passwordController.text,
          "full_name": _nameController.text.trim(),
        }),
      );

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        final token = data['access_token'];

        final parts = token.split('.');
        String? userId;
        if (parts.length == 3) {
          final payload = jsonDecode(
            utf8.decode(base64Url.decode(base64Url.normalize(parts[1]))),
          );
          userId = payload['sub'];
        }

        if (userId != null) {
          await AuthService.saveSession(token, userId);
          if (mounted) context.go('/chat');
        }
      } else {
        setState(() {
          _error = jsonDecode(response.body)['detail'] ?? 'Registration failed';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Connection error';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Create Account')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: 'Full Name'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _emailController,
              decoration: const InputDecoration(labelText: 'Email'),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: 'Password'),
              obscureText: true,
            ),
            const SizedBox(height: 24),
            InlineErrorText(_error),
            PrimaryLoadingButton(
              isLoading: _isLoading,
              onPressed: _register,
              label: 'Create Account',
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () => context.go('/login'),
              child: const Text('Already have an account? Sign In'),
            ),
          ],
        ),
      ),
    );
  }
}