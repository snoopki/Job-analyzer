import { Card, Text, Title, Button} from '@mantine/core';

function JobCard({ job }) {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Title order={4}>{job.title}</Title>
      <Text size="sm" c="dimmed" mb="xs">
        {job.company}
      </Text>
      <Text size="sm" mb="xs">
        רמת ניסיון: <Text span fw={700}>{job.level}</Text>
      </Text>
      <Text size="sm" mb="md">
        מידת התאמה: <Text span fw={700} c="teal">{job.match_percentage}%</Text>
      </Text>

      <Button
        variant="light"
        color="blue"
        fullWidth
        mt="md" 
        radius="md"
        component="a" 
        href={job.link}
        target="_blank"
        rel="noopener noreferrer"
      >
        צפה במשרה
      </Button>
    </Card>
  );
}

export default JobCard;