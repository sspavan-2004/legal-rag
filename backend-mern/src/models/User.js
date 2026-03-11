import mongoose from "mongoose";

const userSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true,
    },
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
    },
    provider: {
      type: String,
      default: "local",
    },
    googleId: {
      type: String,
      unique: true,
      sparse: true,
    },
    avatarUrl: {
      type: String,
      default: "",
    },
    password: {
      type: String,
      validate: {
        validator: function(v) {
          // Only validate if password is being set (not undefined/null)
          // For OAuth users, password will be undefined
          if (v === undefined || v === null) return true;
          return v.length >= 6;
        },
        message: 'Password must be at least 6 characters long'
      }
    },
  },
  { timestamps: true }
);

export default mongoose.model("User", userSchema);
