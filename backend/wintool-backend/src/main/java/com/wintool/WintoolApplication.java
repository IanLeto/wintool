package com.wintool;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Wintool 后端应用主类
 * 
 * @author Wintool Team
 * @version 1.0.0
 */
@SpringBootApplication
public class WintoolApplication {

    public static void main(String[] args) {
        SpringApplication.run(WintoolApplication.class, args);
        System.out.println("\n========================================");
        System.out.println("  Wintool Backend 启动成功！");
        System.out.println("  访问地址: http://localhost:8080");
        System.out.println("  API 文档: http://localhost:8080/swagger-ui.html");
        System.out.println("========================================\n");
    }
}
