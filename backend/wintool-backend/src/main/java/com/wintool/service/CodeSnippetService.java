package com.wintool.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.wintool.entity.CodeSnippet;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 代码片段服务类
 * 负责代码片段的增删改查和本地文件持久化
 */
@Service
public class CodeSnippetService {
    
    private static final Logger logger = LoggerFactory.getLogger(CodeSnippetService.class);
    
    // 数据文件路径 - 保存在项目根目录的 code_snippets 文件夹
    private static final String DATA_DIR = "code_snippets";
    private static final String DATA_FILE = "snippets.json";
    
    private final ObjectMapper objectMapper;
    private final File dataFile;
    private List<CodeSnippet> snippets;
    
    public CodeSnippetService() {
        this.objectMapper = new ObjectMapper();
        this.objectMapper.registerModule(new JavaTimeModule());
        
        // 创建数据目录
        File dataDir = new File(DATA_DIR);
        if (!dataDir.exists()) {
            dataDir.mkdirs();
            logger.info("创建代码片段数据目录: {}", dataDir.getAbsolutePath());
        }
        
        this.dataFile = new File(dataDir, DATA_FILE);
        this.snippets = new ArrayList<>();
    }
    
    /**
     * 初始化 - 从文件加载数据
     */
    @PostConstruct
    public void init() {
        loadFromFile();
        logger.info("代码片段服务初始化完成，加载了 {} 个片段", snippets.size());
    }
    
    /**
     * 获取所有代码片段
     */
    public List<CodeSnippet> getAllSnippets() {
        return new ArrayList<>(snippets);
    }
    
    /**
     * 根据ID获取代码片段
     */
    public CodeSnippet getSnippetById(Long id) {
        return snippets.stream()
                .filter(s -> s.getId().equals(id))
                .findFirst()
                .orElse(null);
    }
    
    /**
     * 搜索代码片段
     */
    public List<CodeSnippet> searchSnippets(String keyword) {
        if (keyword == null || keyword.trim().isEmpty()) {
            return getAllSnippets();
        }
        
        String lowerKeyword = keyword.toLowerCase();
        return snippets.stream()
                .filter(s -> 
                    s.getTitle().toLowerCase().contains(lowerKeyword) ||
                    s.getLanguage().toLowerCase().contains(lowerKeyword) ||
                    s.getCode().toLowerCase().contains(lowerKeyword) ||
                    (s.getTags() != null && s.getTags().stream()
                            .anyMatch(tag -> tag.toLowerCase().contains(lowerKeyword)))
                )
                .collect(Collectors.toList());
    }
    
    /**
     * 按语言筛选
     */
    public List<CodeSnippet> getSnippetsByLanguage(String language) {
        return snippets.stream()
                .filter(s -> s.getLanguage().equalsIgnoreCase(language))
                .collect(Collectors.toList());
    }
    
    /**
     * 创建代码片段
     */
    public CodeSnippet createSnippet(CodeSnippet snippet) {
        // 生成ID
        Long newId = snippets.stream()
                .mapToLong(CodeSnippet::getId)
                .max()
                .orElse(0L) + 1;
        
        snippet.setId(newId);
        snippet.setCreatedAt(LocalDateTime.now());
        snippet.setUpdatedAt(LocalDateTime.now());
        
        snippets.add(0, snippet); // 添加到列表开头
        saveToFile();
        
        logger.info("创建代码片段: {}", snippet.getTitle());
        return snippet;
    }
    
    /**
     * 更新代码片段
     */
    public CodeSnippet updateSnippet(Long id, CodeSnippet updatedSnippet) {
        for (int i = 0; i < snippets.size(); i++) {
            CodeSnippet snippet = snippets.get(i);
            if (snippet.getId().equals(id)) {
                updatedSnippet.setId(id);
                updatedSnippet.setCreatedAt(snippet.getCreatedAt());
                updatedSnippet.setUpdatedAt(LocalDateTime.now());
                snippets.set(i, updatedSnippet);
                saveToFile();
                
                logger.info("更新代码片段: {}", updatedSnippet.getTitle());
                return updatedSnippet;
            }
        }
        return null;
    }
    
    /**
     * 删除代码片段
     */
    public boolean deleteSnippet(Long id) {
        boolean removed = snippets.removeIf(s -> s.getId().equals(id));
        if (removed) {
            saveToFile();
            logger.info("删除代码片段: ID={}", id);
        }
        return removed;
    }
    
    /**
     * 从文件加载数据
     */
    private void loadFromFile() {
        if (!dataFile.exists()) {
            logger.info("数据文件不存在，将创建新文件: {}", dataFile.getAbsolutePath());
            snippets = new ArrayList<>();
            return;
        }
        
        try {
            snippets = objectMapper.readValue(dataFile, new TypeReference<List<CodeSnippet>>() {});
            logger.info("从文件加载了 {} 个代码片段", snippets.size());
        } catch (IOException e) {
            logger.error("加载代码片段数据失败", e);
            snippets = new ArrayList<>();
        }
    }
    
    /**
     * 保存数据到文件
     */
    private void saveToFile() {
        try {
            objectMapper.writerWithDefaultPrettyPrinter()
                    .writeValue(dataFile, snippets);
            logger.debug("保存 {} 个代码片段到文件", snippets.size());
        } catch (IOException e) {
            logger.error("保存代码片段数据失败", e);
        }
    }
    
    /**
     * 获取所有语言列表
     */
    public List<String> getAllLanguages() {
        return snippets.stream()
                .map(CodeSnippet::getLanguage)
                .distinct()
                .sorted()
                .collect(Collectors.toList());
    }
}
