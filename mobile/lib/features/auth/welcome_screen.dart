import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.psychology_outlined, size: 80, color: scheme.primary),
              const SizedBox(height: 24),
              Text(
                'Mind Companion',
                style: textTheme.displayMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              Text(
                'Your personal AI companion for emotional wellness and self-growth.',
                textAlign: TextAlign.center,
                style: textTheme.bodyLarge?.copyWith(color: scheme.onSurfaceVariant),
              ),
              const SizedBox(height: 48),
              ElevatedButton(
                onPressed: () => context.go('/login'),
                child: const Text('Sign In'),
              ),
              const SizedBox(height: 12),
              OutlinedButton(
                onPressed: () => context.go('/register'),
                child: const Text('Create Account'),
              ),
              const SizedBox(height: 24),
              OutlinedButton.icon(
                onPressed: () {
                  // TODO: Implement Google Sign-In
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Google Sign-In coming soon')),
                  );
                },
                icon: const Icon(Icons.g_mobiledata),
                label: const Text('Continue with Google'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
