package com.yukti.gateway;

import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.time.Duration;

@Configuration
public class LangChain4jConfig {

    @Bean
    public ChatLanguageModel chatLanguageModel() {
        // IMPORTANT: Replace 192.168.29.96 with your actual MSI Edge Expert IP!
        // If Ollama is on the SAME machine as Docker, use: "http://host.docker.internal:11434/v1"
        String aiNodeBaseUrl = "http://192.168.29.96:11434/v1"; 
        
        return OpenAiChatModel.builder()
                .baseUrl(aiNodeBaseUrl)
                .apiKey("dummy") // Ollama/vLLM local setups don't need real keys, but LangChain4j requires a non-empty string
                .modelName("qwen2.5:14b") // Change to "qwen-27b" if using vLLM on port 8000
                .timeout(Duration.ofSeconds(120)) // LLMs can take time to generate
                .build();
    }
}
