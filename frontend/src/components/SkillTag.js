import { Badge } from '@mantine/core';

function SkillTag({ skillName, color }) {
  return (
    <Badge color={color} size="lg" radius="sm" variant="light">
      {skillName}
    </Badge>
  );
}

export default SkillTag;