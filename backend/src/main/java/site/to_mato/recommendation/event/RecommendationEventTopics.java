package site.to_mato.recommendation.event;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;

@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class RecommendationEventTopics {

    public static final String ACTION_LOG = "recommendation.action-log";
}
