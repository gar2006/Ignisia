const mockData = {
  summary: {
    totalStudents: 128,
    clusterCount: 4,
    averageScore: 78,
    completionRate: 94,
  },
  accuracy: [
    { name: 'Correct', value: 62, color: '#22c55e' },
    { name: 'Partial', value: 24, color: '#f59e0b' },
    { name: 'Wrong', value: 14, color: '#ef4444' },
  ],
  clusters: [
    {
      id: 'Cluster A1',
      studentCount: 42,
      assignedMarks: 9,
      keywordsMatched: ['photosynthesis', 'chlorophyll', 'glucose'],
      representativeAnswer:
        'Most students explained photosynthesis as the process where plants use sunlight, chlorophyll, water, and carbon dioxide to form glucose and oxygen.',
      answers: [
        {
          studentId: 'ST-1021',
          text: 'Photosynthesis is how green plants use sunlight and chlorophyll to convert water and carbon dioxide into glucose and oxygen.',
        },
        {
          studentId: 'ST-1058',
          text: 'Plants prepare food by photosynthesis. Chlorophyll absorbs sunlight, then water and carbon dioxide are used to produce glucose.',
        },
        {
          studentId: 'ST-1094',
          text: 'In photosynthesis, the leaf uses chlorophyll and sunlight to make glucose, releasing oxygen as a byproduct.',
        },
      ],
    },
    {
      id: 'Cluster B2',
      studentCount: 33,
      assignedMarks: 7,
      keywordsMatched: ['sunlight', 'carbon dioxide', 'oxygen'],
      representativeAnswer:
        'These answers capture the overall idea of the reaction but miss the role of chlorophyll or the formation of glucose.',
      answers: [
        {
          studentId: 'ST-1106',
          text: 'Plants use sunlight, carbon dioxide, and water to make food and give out oxygen.',
        },
        {
          studentId: 'ST-1113',
          text: 'Photosynthesis needs sunlight and carbon dioxide, and oxygen is released after food is made.',
        },
        {
          studentId: 'ST-1142',
          text: 'The process uses sunlight to change raw materials into plant food and oxygen.',
        },
      ],
    },
    {
      id: 'Cluster C3',
      studentCount: 28,
      assignedMarks: 5,
      keywordsMatched: ['leaves', 'food', 'sunlight'],
      representativeAnswer:
        'This cluster is conceptually close but uses simpler language and leaves out the chemical details required by the rubric.',
      answers: [
        {
          studentId: 'ST-1187',
          text: 'Leaves make food for the plant with the help of sunlight.',
        },
        {
          studentId: 'ST-1201',
          text: 'Plants prepare food in green leaves when sunlight falls on them.',
        },
        {
          studentId: 'ST-1236',
          text: 'Sunlight helps leaves make food that supports plant growth.',
        },
      ],
    },
    {
      id: 'Cluster D4',
      studentCount: 25,
      assignedMarks: 2,
      keywordsMatched: ['oxygen'],
      representativeAnswer:
        'Responses here are fragmented or confused, often mixing respiration with photosynthesis and showing minimal rubric coverage.',
      answers: [
        {
          studentId: 'ST-1268',
          text: 'Plants take oxygen and make food in the roots.',
        },
        {
          studentId: 'ST-1275',
          text: 'Photosynthesis is when oxygen is absorbed and stored inside the stem.',
        },
        {
          studentId: 'ST-1289',
          text: 'Plants breathe oxygen during photosynthesis to make their energy.',
        },
      ],
    },
  ],
}

export default mockData
