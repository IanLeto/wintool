package com.wintool.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Stream;

/**
 * 目录结构导出控制器
 * 
 * @author Wintool Team
 * @version 1.0.0
 */
@Tag(name = "目录结构导出", description = "导出目录树结构")
@RestController
@RequestMapping("/api/directory")
@CrossOrigin(origins = "*")
public class DirectoryController {

    @Operation(summary = "创建目录结构", description = "在目标位置创建相同的空目录结构")
    @PostMapping("/create-structure")
    public Map<String, Object> createDirectoryStructure(@RequestBody CreateStructureRequest request) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            String sourcePath = normalizePath(request.getSourcePath());
            String targetPath = normalizePath(request.getTargetPath());
            
            Path source = Paths.get(sourcePath);
            Path target = Paths.get(targetPath);
            
            // 验证源路径
            if (!Files.exists(source) || !Files.isDirectory(source)) {
                result.put("success", false);
                result.put("message", "源路径不存在或不是目录");
                return result;
            }
            
            // 创建目标根目录
            if (!Files.exists(target)) {
                Files.createDirectories(target);
            }
            
            // 复制目录结构
            int createdCount = copyDirectoryStructure(source, target, request.getMaxDepth(), 0);
            
            result.put("success", true);
            result.put("message", "成功创建 " + createdCount + " 个目录");
            result.put("createdCount", createdCount);
            result.put("targetPath", targetPath);
            
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "创建失败: " + e.getMessage());
        }
        
        return result;
    }
    
    @Operation(summary = "导出目录结构", description = "递归导出指定目录的树形结构")
    @PostMapping("/export")
    public Map<String, Object> exportDirectory(@RequestBody ExportRequest request) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            // 转换路径（处理 Windows 路径）
            String normalizedPath = normalizePath(request.getPath());
            Path path = Paths.get(normalizedPath);
            
            // 验证路径
            if (!Files.exists(path)) {
                result.put("success", false);
                result.put("message", "路径不存在: " + request.getPath());
                return result;
            }
            
            if (!Files.isDirectory(path)) {
                result.put("success", false);
                result.put("message", "不是有效的目录: " + request.getPath());
                return result;
            }
            
            // 导出目录结构
            DirectoryNode tree = buildDirectoryTree(path, request.getMaxDepth(), 0);
            
            result.put("success", true);
            result.put("tree", tree);
            result.put("originalPath", request.getPath());
            result.put("normalizedPath", normalizedPath);
            
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "导出失败: " + e.getMessage());
        }
        
        return result;
    }
    
    /**
     * 复制目录结构（只创建目录，不复制文件）
     */
    private int copyDirectoryStructure(Path source, Path target, Integer maxDepth, int currentDepth) throws Exception {
        int count = 0;
        
        // 检查深度限制
        if (maxDepth != null && maxDepth > 0 && currentDepth >= maxDepth) {
            return count;
        }
        
        try (Stream<Path> stream = Files.list(source)) {
            for (Path sourcePath : stream.toList()) {
                if (Files.isDirectory(sourcePath)) {
                    // 创建对应的目标目录
                    Path targetPath = target.resolve(sourcePath.getFileName());
                    if (!Files.exists(targetPath)) {
                        Files.createDirectory(targetPath);
                        count++;
                    }
                    
                    // 递归处理子目录
                    count += copyDirectoryStructure(sourcePath, targetPath, maxDepth, currentDepth + 1);
                }
            }
        }
        
        return count;
    }
    
    /**
     * 规范化路径（处理 Windows 路径）
     */
    private String normalizePath(String path) {
        if (path == null || path.trim().isEmpty()) {
            return System.getProperty("user.home");
        }
        
        // 处理 Windows 路径 (如 D:\folder -> /mnt/d/folder)
        if (path.matches("^[A-Za-z]:.*")) {
            String drive = path.substring(0, 1).toLowerCase();
            String restPath = path.substring(2).replace("\\", "/");
            return "/mnt/" + drive + restPath;
        }
        
        // 处理反斜杠
        return path.replace("\\", "/");
    }
    
    /**
     * 构建目录树
     */
    private DirectoryNode buildDirectoryTree(Path path, Integer maxDepth, int currentDepth) {
        DirectoryNode node = new DirectoryNode();
        node.setName(path.getFileName() != null ? path.getFileName().toString() : path.toString());
        node.setPath(path.toString());
        node.setType("directory");
        
        // 检查深度限制
        if (maxDepth != null && maxDepth > 0 && currentDepth >= maxDepth) {
            return node;
        }
        
        List<DirectoryNode> children = new ArrayList<>();
        
        try (Stream<Path> stream = Files.list(path)) {
            stream.sorted((p1, p2) -> {
                // 目录优先，然后按名称排序
                boolean isDir1 = Files.isDirectory(p1);
                boolean isDir2 = Files.isDirectory(p2);
                if (isDir1 && !isDir2) return -1;
                if (!isDir1 && isDir2) return 1;
                return p1.getFileName().toString().compareToIgnoreCase(p2.getFileName().toString());
            }).forEach(childPath -> {
                try {
                    if (Files.isDirectory(childPath)) {
                        // 递归处理子目录
                        DirectoryNode childNode = buildDirectoryTree(childPath, maxDepth, currentDepth + 1);
                        children.add(childNode);
                    } else {
                        // 文件节点
                        DirectoryNode fileNode = new DirectoryNode();
                        fileNode.setName(childPath.getFileName().toString());
                        fileNode.setPath(childPath.toString());
                        fileNode.setType("file");
                        fileNode.setSize(Files.size(childPath));
                        children.add(fileNode);
                    }
                } catch (Exception e) {
                    // 忽略无法访问的文件/目录
                }
            });
        } catch (Exception e) {
            // 忽略无法读取的目录
        }
        
        node.setChildren(children);
        node.setChildCount(children.size());
        
        return node;
    }
    
    /**
     * 导出请求
     */
    public static class ExportRequest {
        private String path;
        private Integer maxDepth; // null 表示无限制
        
        public String getPath() {
            return path;
        }
        
        public void setPath(String path) {
            this.path = path;
        }
        
        public Integer getMaxDepth() {
            return maxDepth;
        }
        
        public void setMaxDepth(Integer maxDepth) {
            this.maxDepth = maxDepth;
        }
    }
    
    /**
     * 创建目录结构请求
     */
    public static class CreateStructureRequest {
        private String sourcePath;
        private String targetPath;
        private Integer maxDepth;
        
        public String getSourcePath() {
            return sourcePath;
        }
        
        public void setSourcePath(String sourcePath) {
            this.sourcePath = sourcePath;
        }
        
        public String getTargetPath() {
            return targetPath;
        }
        
        public void setTargetPath(String targetPath) {
            this.targetPath = targetPath;
        }
        
        public Integer getMaxDepth() {
            return maxDepth;
        }
        
        public void setMaxDepth(Integer maxDepth) {
            this.maxDepth = maxDepth;
        }
    }
    
    /**
     * 目录节点
     */
    public static class DirectoryNode {
        private String name;
        private String path;
        private String type; // "directory" or "file"
        private Long size;
        private Integer childCount;
        private List<DirectoryNode> children;
        
        public String getName() {
            return name;
        }
        
        public void setName(String name) {
            this.name = name;
        }
        
        public String getPath() {
            return path;
        }
        
        public void setPath(String path) {
            this.path = path;
        }
        
        public String getType() {
            return type;
        }
        
        public void setType(String type) {
            this.type = type;
        }
        
        public Long getSize() {
            return size;
        }
        
        public void setSize(Long size) {
            this.size = size;
        }
        
        public Integer getChildCount() {
            return childCount;
        }
        
        public void setChildCount(Integer childCount) {
            this.childCount = childCount;
        }
        
        public List<DirectoryNode> getChildren() {
            return children;
        }
        
        public void setChildren(List<DirectoryNode> children) {
            this.children = children;
        }
    }
}
