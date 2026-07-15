import 'package:flutter/material.dart';

/// "Dusk" palette — soft lavender-indigo primary, warm apricot accent.
class DuskColors {
  DuskColors._();

  // Light mode
  static const Color primary = Color(0xFF6C6CA0);
  static const Color onPrimary = Color(0xFFF4F3FA);
  static const Color primaryContainer = Color(0xFFE3E1F0);
  static const Color onPrimaryContainer = Color(0xFF201F36);

  static const Color accent = Color(0xFFE39A6E);
  static const Color onAccent = Color(0xFF341C0C);
  static const Color accentContainer = Color(0xFFFBE4D2);
  static const Color onAccentContainer = Color(0xFF93502A);

  static const Color background = Color(0xFFF3F2F7);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFEAE8F2);
  static const Color outline = Color(0xFFDEDCE8);

  static const Color ink = Color(0xFF26243A);
  static const Color muted = Color(0xFF716F8A);

  static const Color error = Color(0xFFB3455D);
  static const Color onError = Color(0xFFFFFFFF);
  static const Color errorContainer = Color(0xFFF6DCE1);
  static const Color onErrorContainer = Color(0xFF5C1B30);

  // Dark mode
  static const Color primaryDark = Color(0xFFACA9D9);
  static const Color onPrimaryDark = Color(0xFF221F3B);
  static const Color primaryContainerDark = Color(0xFF3B3860);
  static const Color onPrimaryContainerDark = Color(0xFFE3E1F0);

  static const Color accentDark = Color(0xFFE8B48C);
  static const Color onAccentDark = Color(0xFF432209);
  static const Color accentContainerDark = Color(0xFF6B441F);
  static const Color onAccentContainerDark = Color(0xFFFBE4D2);

  static const Color backgroundDark = Color(0xFF17151F);
  static const Color surfaceDark = Color(0xFF201E2C);
  static const Color surfaceVariantDark = Color(0xFF35334A);
  static const Color outlineDark = Color(0xFF454259);

  static const Color inkDark = Color(0xFFE7E5F0);
  static const Color mutedDark = Color(0xFFA5A2BE);

  static const Color errorDark = Color(0xFFE6A0B2);
  static const Color onErrorDark = Color(0xFF4C0F22);
  static const Color errorContainerDark = Color(0xFF6E2740);
  static const Color onErrorContainerDark = Color(0xFFF6DCE1);
}

class AppColorSchemes {
  AppColorSchemes._();

  static const ColorScheme light = ColorScheme.light(
    primary: DuskColors.primary,
    onPrimary: DuskColors.onPrimary,
    primaryContainer: DuskColors.primaryContainer,
    onPrimaryContainer: DuskColors.onPrimaryContainer,
    secondary: DuskColors.accent,
    onSecondary: DuskColors.onAccent,
    secondaryContainer: DuskColors.accentContainer,
    onSecondaryContainer: DuskColors.onAccentContainer,
    surface: DuskColors.surface,
    onSurface: DuskColors.ink,
    surfaceContainerHighest: DuskColors.surfaceVariant,
    onSurfaceVariant: DuskColors.muted,
    outline: DuskColors.outline,
    error: DuskColors.error,
    onError: DuskColors.onError,
    errorContainer: DuskColors.errorContainer,
    onErrorContainer: DuskColors.onErrorContainer,
  );

  static const ColorScheme dark = ColorScheme.dark(
    primary: DuskColors.primaryDark,
    onPrimary: DuskColors.onPrimaryDark,
    primaryContainer: DuskColors.primaryContainerDark,
    onPrimaryContainer: DuskColors.onPrimaryContainerDark,
    secondary: DuskColors.accentDark,
    onSecondary: DuskColors.onAccentDark,
    secondaryContainer: DuskColors.accentContainerDark,
    onSecondaryContainer: DuskColors.onAccentContainerDark,
    surface: DuskColors.surfaceDark,
    onSurface: DuskColors.inkDark,
    surfaceContainerHighest: DuskColors.surfaceVariantDark,
    onSurfaceVariant: DuskColors.mutedDark,
    outline: DuskColors.outlineDark,
    error: DuskColors.errorDark,
    onError: DuskColors.onErrorDark,
    errorContainer: DuskColors.errorContainerDark,
    onErrorContainer: DuskColors.onErrorContainerDark,
  );
}
