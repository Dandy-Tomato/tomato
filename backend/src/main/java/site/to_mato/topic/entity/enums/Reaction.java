package site.to_mato.topic.entity.enums;

import lombok.Getter;

@Getter
public enum Reaction {
    LIKE(1),
    DISLIKE(-1);

    private final int score;

    Reaction(int score) {
        this.score = score;
    }

}
