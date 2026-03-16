package site.to_mato.recommendation.service;

import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;

import org.springframework.transaction.annotation.Transactional;

import lombok.RequiredArgsConstructor;
import site.to_mato.project.entity.Project;
import site.to_mato.project.repository.ProjectDomainRepository;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.recommendation.dto.response.RecommendationResponse;
import site.to_mato.recommendation.client.RecommendationClient;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class RecommendationService {

    private final ProjectDomainRepository projectDomainRepository;
    private final ProjectRepository projectRepository;
    private final RecommendationClient recommendationClient;

    // 프로젝트 별 추천 주제 조회
    public List<RecommendationResponse> getRecommendationsByProjectId(Long projectId) {

        // 도메인 id 목록
        List<Long> domainIds = projectDomainRepository.findByProjectId(projectId)
                .stream()
                .map(domain -> domain.getDomain().getId())
                .collect(Collectors.toList());

        // 프로젝트 선호 임베딩 벡터
        Project project = projectRepository.findById(Objects.requireNonNull(projectId)).orElseThrow();
        List<Float> preferenceEmbeddings = project.getPreferenceEmbeddings();

        return recommendationClient.getRecommendations(projectId, domainIds, preferenceEmbeddings);
    }
}
