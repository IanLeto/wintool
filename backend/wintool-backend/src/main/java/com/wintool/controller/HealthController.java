package com.wintool.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

/**
 * 健康检查控制器
 * 
 * @author Wintool Team
 * @version 1.0.0
 */
@Tag(name = "健康检查", description = "系统健康检查接口")
@RestController
@RequestMapping("/api")
public class HealthController {

    @Operation(summary = "健康检查", description = "检查系统是否正常运行")
    @GetMapping("/health")
    public Map<String, Object> health() {
        Map<String, Object> result = new HashMap<>();
        result.put("status", "UP");
        result.put("application", "wintool-backend");
        result.put("version", "1.0.0");
        result.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        return result;
    }

    @Operation(summary = "欢迎页面", description = "获取欢迎信息")
    @GetMapping("/welcome")
    public Map<String, Object> welcome() {
        Map<String, Object> result = new HashMap<>();
        result.put("message", "欢迎使用 Wintool 文件处理工具集合！");
        result.put("description", "这是一个基于 Spring Boot 的后端服务");
        result.put("docs", "访问 /swagger-ui.html 查看 API 文档");
        result.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        return result;
    }
}
