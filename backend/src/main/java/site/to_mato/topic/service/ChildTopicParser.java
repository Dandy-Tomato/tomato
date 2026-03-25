package site.to_mato.topic.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ChildTopicParser {

    public static ParsedTopic parse(String llmResponse, String fallbackTitle, ObjectMapper objectMapper) {
        String title = fallbackTitle;
        String content = llmResponse;

        try {
            String cleaned = preprocess(llmResponse);

            JsonNode jsonNode = tryParseJson(cleaned, objectMapper);

            // JSON 문자열로 한번 더 감싸진 경우 (이중 파싱)
            if (jsonNode != null && jsonNode.isTextual()) {
                jsonNode = objectMapper.readTree(jsonNode.asText());
            }

            if (jsonNode != null && jsonNode.has("title") && jsonNode.has("content")) {
                title = jsonNode.get("title").asText();
                content = jsonNode.get("content").asText();
            }

        } catch (Exception e) {
            log.error("Failed to parse LLM response. Using fallback.", e);
        }

        // 줄바꿈 복원
        content = content.replace("\\n", "\n");

        return new ParsedTopic(title, content);
    }

    /**
     * 전처리: 코드블록 제거 + trim
     */
    private static String preprocess(String response) {
        if (response == null) return "";

        return response
                .replaceAll("```json", "")
                .replaceAll("```", "")
                .trim();
    }

    /**
     * JSON 추출 및 파싱
     */
    private static JsonNode tryParseJson(String response, ObjectMapper objectMapper) {
        try {
            // 1️⃣ 전체가 JSON인 경우
            if (response.startsWith("{") && response.endsWith("}")) {
                return objectMapper.readTree(response);
            }

            // 2️⃣ 문자열 안에 JSON 있는 경우
            int start = response.indexOf("{");
            int end = response.lastIndexOf("}");

            if (start != -1 && end != -1 && end > start) {
                String jsonSubstring = response.substring(start, end + 1);
                return objectMapper.readTree(jsonSubstring);
            }

        } catch (Exception e) {
            log.warn("JSON parsing failed at tryParseJson", e);
        }

        return null;
    }

    public record ParsedTopic(String title, String content) {}
}