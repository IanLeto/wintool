package com.wintool.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * 原型预览控制器
 * 用于提供 prototypes 目录下的 HTML 文件访问
 */
@RestController
@RequestMapping("/prototypes")
@CrossOrigin(origins = "*")
public class PrototypeController {

    private static final Logger logger = LoggerFactory.getLogger(PrototypeController.class);
    private static final String PROTOTYPES_DIR = "../../prototypes";

    /**
     * 获取原型文件
     * @param filename 文件名
     * @return 文件内容
     */
    @GetMapping("/{filename:.+}")
    public ResponseEntity<Resource> getPrototype(@PathVariable String filename) {
        try {
            logger.info("请求原型文件: {}", filename);
            
            // 构建文件路径（相对于 backend/wintool-backend 目录，需要向上两级到项目根目录）
            File file = new File(PROTOTYPES_DIR, filename);
            
            if (!file.exists() || !file.canRead()) {
                logger.warn("文件不存在或不可读: {}", file.getAbsolutePath());
                return ResponseEntity.notFound().build();
            }

            logger.info("找到文件: {}", file.getAbsolutePath());
            
            Resource resource = new FileSystemResource(file);

            // 确定内容类型
            String contentType = Files.probeContentType(file.toPath());
            if (contentType == null) {
                contentType = "text/html";
            }

            return ResponseEntity.ok()
                    .contentType(MediaType.parseMediaType(contentType))
                    .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + file.getName() + "\"")
                    .body(resource);

        } catch (IOException e) {
            logger.error("读取原型文件失败: {}", filename, e);
            return ResponseEntity.internalServerError().build();
        }
    }
}
