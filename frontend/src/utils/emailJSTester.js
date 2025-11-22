// EmailJS Template Parameter Tester
// This will help identify what parameters your EmailJS template expects

export const testEmailJSParameters = async () => {
  console.log('🔍 Testing EmailJS Template Parameters...');
  
  // Test different common parameter combinations
  const testCases = [
    {
      name: 'Standard Parameters',
      params: {
        to_email: 'saranyasumathy5@gmail.com',
        from_name: 'ATM Surveillance System',
        subject: 'Test Email',
        message: 'This is a test message'
      }
    },
    {
      name: 'Alternative Recipient Names',
      params: {
        to_name: 'saranyasumathy5@gmail.com',
        user_email: 'saranyasumathy5@gmail.com',
        email: 'saranyasumathy5@gmail.com',
        recipient: 'saranyasumathy5@gmail.com',
        from_name: 'ATM Surveillance System',
        subject: 'Test Email',
        message: 'This is a test message'
      }
    },
    {
      name: 'Minimal Parameters',
      params: {
        to_email: 'saranyasumathy5@gmail.com',
        message: 'Test message'
      }
    }
  ];

  for (const testCase of testCases) {
    console.log(`\n🧪 Testing: ${testCase.name}`);
    console.log('Parameters:', testCase.params);
    
    try {
      const response = await emailjs.send(
        'service_ekpo2ws',
        'template_y5dqc4w',
        testCase.params
      );
      
      console.log('✅ SUCCESS:', testCase.name);
      console.log('Response:', response);
      return { success: true, workingParams: testCase.params };
      
    } catch (error) {
      console.log('❌ FAILED:', testCase.name);
      console.log('Error:', error.text || error.message);
      
      if (error.text && error.text.includes('recipients address is empty')) {
        console.log('💡 Hint: Template expects different recipient parameter name');
      }
    }
  }
  
  console.log('\n🔧 Next Steps:');
  console.log('1. Check your EmailJS dashboard');
  console.log('2. Look at template template_y5dqc4w');
  console.log('3. See what parameters it uses (e.g., {{to_email}}, {{user_email}}, etc.)');
  console.log('4. Update the parameter names in the code');
  
  return { success: false, message: 'All test cases failed' };
};

// Quick test function
export const quickEmailJSTest = () => {
  console.log('🚀 Quick EmailJS Test');
  console.log('Run this in browser console:');
  console.log('testEmailJSParameters()');
  
  return testEmailJSParameters();
};
