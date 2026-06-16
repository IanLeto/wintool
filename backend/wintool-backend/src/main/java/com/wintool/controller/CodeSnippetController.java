package com.wintool.controller;

import com.wintool.entity.CodeSnippet;
import com.wintool.service.CodeSnippetService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 代码片段控制器
 * 提供代码片段的 RESTful API
 */
@RestController
@RequestMapping("/api/code-snippets")
@CrossOrigin(origins = "*")
public class CodeSnippetController {
    
    private static final Logger logger = LoggerFactory.getLogger(CodeSnippetController.class);
    
    @Autowired
    private CodeSnippetService codeSnippetService;
    
    /**
     * 获取所有代码片段
     */
    @GetMapping
    public ResponseEntity<Map<String, Object>> getAllSnippets(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String language) {
        
        try {
            List<CodeSnippet> snippets;
            
            if (keyword != null && !keyword.trim().isEmpty()) {
                snippets = codeSnippetService.searchSnippets(keyword);
                logger.info("搜索代码片段，关键词: {}, 结果数: {}", keyword, snippets.size());
            } else if (language != null && !language.trim().isEmpty()) {
                snippets = codeSnippetService.getSnippetsByLanguage(language);
                logger.info("按语言筛选代码片段，语言: {}, 结果数: {}", language, snippets.size());
            } else {
                snippets = codeSnippetService.getAllSnippets();
                logger.info("获取所有代码片段，总数: {}", snippets.size());
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", snippets);
            response.put("total", snippets.size());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("获取代码片段失败", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("获取代码片段失败: " + e.getMessage()));
        }
    }
    
    /**
     * 根据ID获取代码片段
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getSnippetById(@PathVariable Long id) {
        try {
            CodeSnippet snippet = codeSnippetService.getSnippetById(id);
            
            if (snippet == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(createErrorResponse("代码片段不存在"));
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", snippet);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("获取代码片段失败, ID: {}", id, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("获取代码片段失败: " + e.getMessage()));
        }
    }
    
    /**
     * 创建代码片段
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createSnippet(@RequestBody CodeSnippet snippet) {
        try {
            // 验证必填字段
            if (snippet.getTitle() == null || snippet.getTitle().trim().isEmpty()) {
                return ResponseEntity.badRequest()
                        .body(createErrorResponse("标题不能为空"));
            }
            if (snippet.getCode() == null || snippet.getCode().trim().isEmpty()) {
                return ResponseEntity.badRequest()
                        .body(createErrorResponse("代码不能为空"));
            }
            
            CodeSnippet created = codeSnippetService.createSnippet(snippet);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", created);
            response.put("message", "创建成功");
            
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (Exception e) {
            logger.error("创建代码片段失败", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("创建代码片段失败: " + e.getMessage()));
        }
    }
    
    /**
     * 更新代码片段
     */
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateSnippet(
            @PathVariable Long id,
            @RequestBody CodeSnippet snippet) {
        
        try {
            // 验证必填字段
            if (snippet.getTitle() == null || snippet.getTitle().trim().isEmpty()) {
                return ResponseEntity.badRequest()
                        .body(createErrorResponse("标题不能为空"));
            }
            if (snippet.getCode() == null || snippet.getCode().trim().isEmpty()) {
                return ResponseEntity.badRequest()
                        .body(createErrorResponse("代码不能为空"));
            }
            
            CodeSnippet updated = codeSnippetService.updateSnippet(id, snippet);
            
            if (updated == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(createErrorResponse("代码片段不存在"));
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", updated);
            response.put("message", "更新成功");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("更新代码片段失败, ID: {}", id, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("更新代码片段失败: " + e.getMessage()));
        }
    }
    
    /**
     * 删除代码片段
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteSnippet(@PathVariable Long id) {
        try {
            boolean deleted = codeSnippetService.deleteSnippet(id);
            
            if (!deleted) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(createErrorResponse("代码片段不存在"));
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "删除成功");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("删除代码片段失败, ID: {}", id, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("删除代码片段失败: " + e.getMessage()));
        }
    }
    
    /**
     * 获取所有语言列表
     */
    @GetMapping("/languages")
    public ResponseEntity<Map<String, Object>> getAllLanguages() {
        try {
            List<String> languages = codeSnippetService.getAllLanguages();
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", languages);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("获取语言列表失败", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("获取语言列表失败: " + e.getMessage()));
        }
    }
    
    /**
     * 创建错误响应
     */
    private Map<String, Object> createErrorResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("message", message);
        return response;
    }
}
