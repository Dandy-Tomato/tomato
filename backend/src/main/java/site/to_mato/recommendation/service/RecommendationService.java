package site.to_mato.recommendation.service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import org.springframework.transaction.annotation.Transactional;

import lombok.RequiredArgsConstructor;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.project.entity.Project;
import site.to_mato.project.repository.ProjectDomainRepository;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.recommendation.dto.request.RecommendationRequest;
import site.to_mato.recommendation.dto.response.RecommendationApiResponse;
import site.to_mato.recommendation.dto.response.RecommendationResponse;
import site.to_mato.recommendation.client.RecommendationClient;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class RecommendationService {

    private final ProjectDomainRepository projectDomainRepository;
    private final ProjectRepository projectRepository;
    private final RecommendationClient recommendationClient;

    // 프로젝트 별 추천 주제 조회
    public List<RecommendationResponse> getRecommendationsByProjectId(Long projectId) {

        Project project = projectRepository.findById(projectId).orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_NOT_FOUND));

        log.info("[프로젝트 조회 완료] projectId={}", projectId);  // 추가

        List<Long> domainIds = projectDomainRepository.findByProjectId(projectId).stream().map(projectDomain -> projectDomain.getDomain().getId()).toList();

        log.info("[도메인 조회 완료] domainIds={}", domainIds);  // 추가

        List<Float> preferenceEmbedding = null;
        Optional<String> embeddingStr = projectRepository.findPreferenceEmbeddingById(projectId);
        if (embeddingStr.isPresent()) {
            String cleaned = embeddingStr.get().replaceAll("[\\[\\]\\s]", "");
            preferenceEmbedding = Arrays.stream(cleaned.split(","))
                    .map(Float::parseFloat)
                    .collect(Collectors.toList());
        }

        RecommendationRequest request = new RecommendationRequest(
                projectId,
                domainIds,
                preferenceEmbedding
        );

        RecommendationApiResponse apiResponse = recommendationClient.getRecommendations(request);

        return apiResponse.data();
    }
}
