package site.to_mato.recommendation.dto.request;

import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class RecommendationRequest {
    private Long projectId;
    private List<Long> domainIds;
    private List<Float> preferenceEmbeddings;
}
