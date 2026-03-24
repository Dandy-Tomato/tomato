package site.to_mato.recommendation.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import site.to_mato.recommendation.dto.request.RecommendationRequest;
import site.to_mato.recommendation.dto.response.RecommendationApiResponse;

@Component
@RequiredArgsConstructor
@Slf4j
public class RecommendationClient {

    private final RestTemplate restTemplate;

    @Value("${fastapi.url}")
    private String fastApiUrl;

    public RecommendationApiResponse getRecommendations(RecommendationRequest request) {
        log.info("[FastAPI URL] {}", fastApiUrl);  // 이거 추가
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<RecommendationRequest> entity = new HttpEntity<>(request, headers);

        ResponseEntity<RecommendationApiResponse> response = restTemplate.exchange(
                fastApiUrl + "/recommendations",
                HttpMethod.POST,
                entity,
                new ParameterizedTypeReference<RecommendationApiResponse>() {
                }
        );

        return response.getBody();
    }
}