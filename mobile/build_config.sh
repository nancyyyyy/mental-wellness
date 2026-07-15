#!/bin/bash
cat > lib/core/api_config.dart << EOF
class ApiConfig {
  static const String baseUrl = "${API_BASE_URL}";
}
EOF
echo "api_config.dart created with baseUrl: ${API_BASE_URL}"