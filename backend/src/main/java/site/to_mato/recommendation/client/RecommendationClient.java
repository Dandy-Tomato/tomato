package site.to_mato.recommendation.client;

import java.util.List;

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
import site.to_mato.recommendation.dto.request.RecommendationRequest;
import site.to_mato.recommendation.dto.response.RecommendationResponse;

@Component
@RequiredArgsConstructor
public class RecommendationClient {

    private final RestTemplate restTemplate;

    @Value("${fastapi.url}")
    private String fastApiUrl;

    public List<RecommendationResponse> getRecommendations(Long projectId, List<Long> domainIds,
            List<Float> preferenceEmbeddings) {
        String url = fastApiUrl + "/recommendations";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        RecommendationRequest request = new RecommendationRequest(projectId, domainIds, preferenceEmbeddings);
        HttpEntity<RecommendationRequest> entity = new HttpEntity<>(request, headers);

        ResponseEntity<List<RecommendationResponse>> response = restTemplate.exchange(url, HttpMethod.valueOf("POST"),
                entity,
                new ParameterizedTypeReference<List<RecommendationResponse>>() {
                });

        return response.getBody();
    }
}