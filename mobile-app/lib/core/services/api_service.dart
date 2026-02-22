import 'package:dio/dio.dart';
import '../config/app_config.dart';

class ApiService {
  final Dio dio = Dio(BaseOptions(baseUrl: AppConfig.apiBaseUrl));
}
