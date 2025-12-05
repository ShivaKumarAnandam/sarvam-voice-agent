"""
Quick test script to verify your environment setup
Run this before starting the server to check if all credentials are valid
"""

import os
from dotenv import load_dotenv
from loguru import logger

def test_env_variables():
    """Check if all required environment variables are set"""
    logger.info("🔍 Checking environment variables...")
    
    load_dotenv()
    
    required_vars = {
        "SARVAM_API_KEY": "Sarvam AI API Key",
        "TWILIO_ACCOUNT_SID": "Twilio Account SID",
        "TWILIO_AUTH_TOKEN": "Twilio Auth Token",
        "TWILIO_PHONE_NUMBER": "Twilio Phone Number"
    }
    
    missing = []
    placeholder = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append(f"  ❌ {var} ({description})")
        elif "your_" in value or "xxxxx" in value or value == "+1234567890":
            placeholder.append(f"  ⚠️  {var} ({description}) - Still has placeholder value")
        else:
            logger.info(f"  ✅ {var} is set")
    
    if missing:
        logger.error("\n❌ Missing environment variables:")
        for m in missing:
            logger.error(m)
        return False
    
    if placeholder:
        logger.warning("\n⚠️  Placeholder values detected:")
        for p in placeholder:
            logger.warning(p)
        logger.warning("\nPlease update .env file with your actual credentials")
        return False
    
    logger.success("\n✅ All environment variables are set!")
    return True


def test_sarvam_api():
    """Test Sarvam AI API connection"""
    logger.info("\n🔍 Testing Sarvam AI API...")
    
    try:
        import asyncio
        from sarvam_ai import SarvamAI
        
        async def test():
            try:
                sarvam = SarvamAI()
                logger.info("  ✅ Sarvam AI client initialized")
                
                # Test a simple TTS call
                logger.info("  🎵 Testing TTS API...")
                audio = await sarvam.text_to_speech("Hello", "en-IN")
                if audio and len(audio) > 0:
                    logger.success(f"  ✅ TTS API working! Generated {len(audio)} bytes")
                else:
                    logger.error("  ❌ TTS API returned empty audio")
                    return False
                
                await sarvam.close()
                return True
            except ValueError as e:
                logger.error(f"  ❌ Configuration error: {e}")
                return False
            except Exception as e:
                logger.error(f"  ❌ API error: {e}")
                return False
        
        result = asyncio.run(test())
        return result
    
    except ImportError as e:
        logger.error(f"  ❌ Missing dependencies: {e}")
        logger.info("  💡 Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"  ❌ Unexpected error: {e}")
        return False


def test_twilio_credentials():
    """Test Twilio credentials"""
    logger.info("\n🔍 Testing Twilio credentials...")
    
    try:
        from twilio.rest import Client
        
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        
        # Try to fetch account info
        account = client.api.accounts(os.getenv("TWILIO_ACCOUNT_SID")).fetch()
        logger.success(f"  ✅ Twilio credentials valid!")
        logger.info(f"  📊 Account Status: {account.status}")
        logger.info(f"  📞 Phone Number: {os.getenv('TWILIO_PHONE_NUMBER')}")
        
        return True
    
    except Exception as e:
        logger.error(f"  ❌ Twilio authentication failed: {e}")
        logger.info("  💡 Check your TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN")
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("🚀 Sarvam Voice Agent - Setup Verification")
    logger.info("=" * 60)
    
    # Test 1: Environment variables
    if not test_env_variables():
        logger.error("\n❌ Setup incomplete. Please configure .env file first.")
        logger.info("\n📖 See SETUP_GUIDE.md for detailed instructions")
        return
    
    # Test 2: Twilio credentials
    twilio_ok = test_twilio_credentials()
    
    # Test 3: Sarvam AI API
    sarvam_ok = test_sarvam_api()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 Test Summary")
    logger.info("=" * 60)
    logger.info(f"  Environment Variables: ✅")
    logger.info(f"  Twilio Credentials: {'✅' if twilio_ok else '❌'}")
    logger.info(f"  Sarvam AI API: {'✅' if sarvam_ok else '❌'}")
    
    if twilio_ok and sarvam_ok:
        logger.success("\n🎉 All tests passed! You're ready to run the server.")
        logger.info("\n📝 Next steps:")
        logger.info("  1. Run: python twilio_server.py")
        logger.info("  2. Expose to internet: ngrok http 8000")
        logger.info("  3. Configure Twilio webhook with your ngrok URL")
        logger.info("  4. Call your Twilio number to test!")
    else:
        logger.error("\n❌ Some tests failed. Please fix the issues above.")
        logger.info("\n📖 See SETUP_GUIDE.md for help")


if __name__ == "__main__":
    main()
