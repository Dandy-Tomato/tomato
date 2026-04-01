package site.to_mato.catalog.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.catalog.entity.Position;

public interface PositionRepository extends JpaRepository<Position, Long> {
}
