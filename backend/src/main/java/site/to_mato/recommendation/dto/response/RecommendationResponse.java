package site.to_mato.recommendation.dto.response;

import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class RecommendationResponse {
    // 추천 결과에서 받아와야하는 값
    // 주제 아이디
    // 주제 제목
    // 주제 설명
    // 예상 개발 기간
    // 추천 팀원 수
    // 난이도
    // 산업 아이디
    // 참조 레포 아이디
    // 추천 점수
    private Long topicId;
    private String topicTitle;
    private String topicDescription;
    private Integer estimatedDevelopmentPeriod;
    private Integer recommendedTeamSize;
    private Integer difficulty;
    private Long industryId;
    private Long referenceRepoId;
    private Double recommendationScore;
}
