import logging
import config

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    filters,
)

from sqlite import store_data

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)

SEARCH_TYPE, BUDGET, LOCATION, NR_ROOMS = range(4)


async def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user input."""
    reply_keyboard = [["BUY", "RENT"]]

    await update.message.reply_text(
        "Hi! My name is Omen, here to save your precious time.\n"
        "You can send /cancel to stop talking to me at any point.\n"
        "Let's start by refining your search. Are you looking to buy or rent?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Buy or Rent?",
        ),
    )

    return SEARCH_TYPE


async def store_search_type_ask_budget(update: Update, context: CallbackContext) -> int:
    """Stores the selected search type and asks for max price."""
    user = update.message.from_user
    user_full_name = update.message.from_user.full_name
    search_type = update.message.text

    store_data(update.message.from_user.id, "full_name", user_full_name)
    store_data(update.message.from_user.id, "search_type", search_type)

    logger.info("Search Type of %s: %s", user.first_name, search_type)

    await update.message.reply_text(
        "Got it! What is your maximum budget for this search?",
        reply_markup=ReplyKeyboardRemove(),
    )

    return BUDGET


async def store_budget_ask_location(update: Update, context: CallbackContext) -> int:
    """Stores the budget and asks for a location."""
    user = update.message.from_user
    budget = int(update.message.text)

    store_data(update.message.from_user.id, "budget", budget)

    logger.info("Budget of %s: %s", user.first_name, budget)
    await update.message.reply_text(
        "Perfect, quickly share your preferred postal codes now, separated by a comma.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return LOCATION


async def store_location_ask_nr_rooms(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks nr of rooms."""
    user = update.message.from_user
    location = update.message.text

    store_data(update.message.from_user.id, "location", location)

    logger.info("Location of %s: %s", user.first_name, location)
    await update.message.reply_text(
        "And the number of rooms you are looking for?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NR_ROOMS


async def close(update: Update, context: CallbackContext, update_checker) -> int:
    """Stores the NR rooms and ends the conversation."""
    user = update.message.from_user
    nr_rooms = int(update.message.text)

    store_data(update.message.from_user.id, "nr_rooms", nr_rooms)

    logger.info("Nr rooms of %s: %s", user.first_name, nr_rooms)

    await update_checker

    await update.message.reply_text(
        "Great, here is what I found already. If I find anything new, I'll let you know.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def conversation_handler(update_checker) -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SEARCH_TYPE: [
                MessageHandler(
                    filters.Regex("^(BUY|RENT)$"), store_search_type_ask_budget
                )
            ],
            BUDGET: [MessageHandler(filters.Regex(r"\d+"), store_budget_ask_location)],
            LOCATION: [
                MessageHandler(filters.Regex(r"\d+"), store_location_ask_nr_rooms)
            ],
            NR_ROOMS: [
                MessageHandler(
                    filters.Regex(r"\d+"),
                    lambda update, context: close(update, context, update_checker),
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=config.CONVERSATION_TIMEOUT,
    )


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config.CHATBOT_TOKEN).build()

    # Add conversation handler with the states SEARCH_TYPE, BUDGET, LOCATION AND NR_ROOMS
    conv_handler = conversation_handler()

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
