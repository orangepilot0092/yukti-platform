package com.yukti.gateway;

import dev.langchain4j.model.chat.ChatLanguageModel;
import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/enterprise")
public class EnterpriseController {

    private final ChatLanguageModel chatModel;

    // Constructor Injection (Spring Best Practice)
    @Autowired
    public EnterpriseController(ChatLanguageModel chatModel) {
        this.chatModel = chatModel;
    }

    @GetMapping("/health")
    public Map<String, String> healthCheck() {
        return Map.of(
            "status", "UP",
            "service", "Yukti Enterprise Gateway (Java 21 + Spring AI)",
            "compliance", "RBI Data Localization Ready"
        );
    }

    @PostMapping("/chat")
    public Map<String, String> enterpriseChat(@RequestBody Map<String, String> request) {
        String prompt = request.getOrDefault("prompt", "Say hello from Java LangChain4j");
        
        // In a real enterprise app, we would add mTLS context, audit logging, and PII masking here.
        String response = chatModel.generate(prompt);
        
        return Map.of(
            "gateway", "Java Spring AI",
            "ai_response", response
        );
    }
}
