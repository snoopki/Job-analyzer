import {
  Paper,
  Box,
  Group,
  SimpleGrid,
  List,
  Text,
  Title as MantineTitle,
  Stack,
  ThemeIcon
} from '@mantine/core';
import ReactMarkdown from 'react-markdown'; 
import JobCard from './JobCard';
import SkillTag from './SkillTag';

const MarkdownRenderer = ({ text }) => {
  return (
    <ReactMarkdown
      components={{
        p: ({ children }) => <Text component="p" mb="sm" style={{ lineHeight: 1.6 }}>{children}</Text>,
        strong: ({ children }) => <Text span fw={700}>{children}</Text>,
        ul: ({ children }) => <List spacing="xs" size="sm" center>{children}</List>,
        li: ({ children }) => <List.Item>{children}</List.Item>,
      }}
    >
      {text || ''} 
    </ReactMarkdown>
  );
};

function AnalysisResults({ results }) {
  
  const recommendation = results?.recommendation || {};
  const details = results?.analysis_details || {};
  const jobs = results?.top_jobs || [];

  return (
    <Box mt="xl">
      <Stack gap="lg">
        <Paper shadow="sm" p={{ base: 'md', md: 'lg' }} withBorder style={{ direction: 'rtl' }}>
          <MantineTitle order={3} c="blue.6" mb="md">✨ ההמלצה של ה-AI</MantineTitle>     
          <MarkdownRenderer text={recommendation.opening} />
          <MarkdownRenderer text={recommendation.gap_analysis_intro} />
          
          <MantineTitle order={4} mt="lg" mb="sm">
            {recommendation.cv_review_title}
          </MantineTitle>
          
          <List spacing="sm" size="sm" icon={
            <ThemeIcon color="blue" size={20} radius="xl">
              <Text size="xs">✓</Text>
            </ThemeIcon>
          }>
            {(recommendation.cv_review_points || []).map((point, i) => (
              <List.Item key={i}>
                <MarkdownRenderer text={point} />
              </List.Item>
            ))}
          </List>
          
          <Box mt="md">
            <MarkdownRenderer text={recommendation.closing} />
          </Box>
        </Paper>

        <Paper shadow="sm" p={{ base: 'md', md: 'lg' }} withBorder style={{ direction: 'rtl' }}>
          <MantineTitle order={3} c="grape.6" mb="md">📊 ניתוח כישורים</MantineTitle>
          
          <MantineTitle order={5} mb="xs">הכישורים שלך:</MantineTitle>
          <Group gap="xs" mb="lg">
            {(details.cv_skills || []).map((skill) => (
              <SkillTag key={skill} skillName={skill} color="green" />
            ))}
          </Group>

          <MantineTitle order={5} mb="xs">פערים מול השוק:</MantineTitle>
          <Group gap="xs">
            {(details.market_gaps || []).map((skill) => (
              <SkillTag key={skill} skillName={skill} color="orange" />
            ))}
          </Group>
        </Paper>

        <Box>
          <MantineTitle order={3} mb="md">🔥 משרות שיכולות להתאים</MantineTitle>
          <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
            {jobs.map((job, index) => (
              <JobCard key={index} job={job} />
            ))}
          </SimpleGrid>
        </Box>
      </Stack>
    </Box>
  );
}

export default AnalysisResults;